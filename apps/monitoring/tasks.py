"""
Celery Tasks - وظایف پس‌زمینه
"""
from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def calculate_cycle_energy_task(self, cycle_id: int):
    """محاسبه انرژی یک سیکل پس از اتمام"""
    try:
        from apps.devices.models import DeviceCycle
        from core.calculators import EnergyCalculator

        cycle = DeviceCycle.objects.get(pk=cycle_id)
        record = EnergyCalculator.save_energy_record(cycle)
        if record:
            logger.info(f"✅ انرژی سیکل #{cycle_id} محاسبه شد: {record.total_cost} ریال")
        return {'success': True, 'cycle_id': cycle_id}
    except Exception as exc:
        logger.error(f"خطا در محاسبه انرژی سیکل {cycle_id}: {exc}")
        self.retry(exc=exc, countdown=60)


@shared_task
def generate_monthly_report(year: int, month: int):
    """تولید گزارش ماهانه انرژی"""
    from apps.devices.models import Device
    from apps.devices.models import DeviceCycle
    from apps.energy.models import EnergyRecord, MonthlyEnergyReport
    from django.db.models import Sum, Count

    devices = Device.objects.filter(is_active=True)
    reports_created = 0

    for device in devices:
        cycles = DeviceCycle.objects.filter(
            device=device,
            status='complete',
            start_time__year=year,
            start_time__month=month,
        )

        if not cycles.exists():
            continue

        agg = EnergyRecord.objects.filter(cycle__in=cycles).aggregate(
            total_kwh=Sum('electricity_kwh'),
            total_water=Sum('water_liter'),
            total_fuel=Sum('fuel_liter'),
            total_cost=Sum('total_cost'),
            total_carbon=Sum('carbon_footprint_kg'),
        )

        waste_agg = cycles.aggregate(
            total_waste=Sum('waste_weight_kg'),
            cycle_count=Count('id'),
        )

        MonthlyEnergyReport.objects.update_or_create(
            device=device, year=year, month=month,
            defaults={
                'total_cycles': waste_agg['cycle_count'] or 0,
                'total_electricity_kwh': agg['total_kwh'] or 0,
                'total_water_liter': agg['total_water'] or 0,
                'total_fuel_liter': agg['total_fuel'] or 0,
                'total_waste_kg': waste_agg['total_waste'] or 0,
                'total_cost': agg['total_cost'] or 0,
                'total_carbon_kg': agg['total_carbon'] or 0,
            }
        )
        reports_created += 1

    logger.info(f"✅ گزارش ماهانه {year}/{month} برای {reports_created} دستگاه ساخته شد")
    return reports_created


@shared_task
def check_device_connectivity():
    """بررسی آنلاین بودن دستگاه‌ها"""
    from apps.devices.models import Device
    from apps.monitoring.models import SensorReading, DeviceAlert
    from django.utils import timezone

    threshold = timezone.now() - timezone.timedelta(minutes=10)
    active_devices = Device.objects.filter(is_active=True, status='online')

    for device in active_devices:
        last_reading = SensorReading.objects.filter(device=device).order_by('-timestamp').first()
        if not last_reading or last_reading.timestamp < threshold:
            device.status = 'offline'
            device.save(update_fields=['status'])

            DeviceAlert.objects.get_or_create(
                device=device,
                alert_type='connectivity',
                is_resolved=False,
                defaults={
                    'severity': 'critical',
                    'message': f'دستگاه {device.name} بیش از ۱۰ دقیقه داده ارسال نکرده است!',
                }
            )
            logger.warning(f"⚠️ دستگاه {device.name} آفلاین شد")


@shared_task
def send_alert_sms(alert_id: int):
    """ارسال پیامک هشدار"""
    from apps.monitoring.models import DeviceAlert
    from django.conf import settings

    try:
        alert = DeviceAlert.objects.get(pk=alert_id)
        api_key = settings.KAVENEGAR_API_KEY
        numbers = [n for n in settings.ALERT_SMS_NUMBERS if n]

        if not api_key or not numbers:
            logger.warning("Kavenegar API key یا شماره‌ها تنظیم نشده")
            return

        import requests
        message = f"هشدار {alert.get_severity_display()}\n{alert.device.name}\n{alert.message}"

        for number in numbers:
            url = f"https://api.kavenegar.com/v1/{api_key}/sms/send.json"
            requests.post(url, data={'receptor': number, 'message': message}, timeout=10)

        alert.sms_sent = True
        alert.save(update_fields=['sms_sent'])
        logger.info(f"✅ SMS هشدار {alert_id} ارسال شد")

    except Exception as e:
        logger.error(f"خطا در ارسال SMS: {e}")


@shared_task
def simulate_device_data():
    """شبیه‌ساز داده برای تست - فقط در محیط توسعه"""
    from django.conf import settings
    if not settings.DEBUG:
        return

    from apps.devices.models import Device
    from core.mqtt_client import simulate_sensor_data, handle_sensor_data

    devices = Device.objects.filter(is_active=True)[:5]
    for device in devices:
        data = simulate_sensor_data(device.pk, device.device_type)
        data['device_id'] = device.serial_number
        handle_sensor_data(data, f"simulate/{device.serial_number}")


@shared_task
def cleanup_old_sensor_data():
    """
    پاک‌سازی داده‌های خام سنسور قدیمی — Data Retention Policy

    سیاست نگه‌داری:
      - داده خام سنسور:        نگه‌داری SENSOR_RAW_RETENTION_DAYS  (پیش‌فرض: 90 روز)
      - هشدارهای حل‌شده:       نگه‌داری ALERT_RETENTION_DAYS        (پیش‌فرض: 365 روز)

    این تسک باید با Celery Beat هر شب یک‌بار اجرا شود.
    """
    from django.conf import settings
    from django.utils import timezone
    from apps.monitoring.models import SensorReading, DeviceAlert

    raw_days   = getattr(settings, 'SENSOR_RAW_RETENTION_DAYS', 90)
    alert_days = getattr(settings, 'ALERT_RETENTION_DAYS', 365)

    raw_cutoff   = timezone.now() - timezone.timedelta(days=raw_days)
    alert_cutoff = timezone.now() - timezone.timedelta(days=alert_days)

    deleted_readings, _ = SensorReading.objects.filter(timestamp__lt=raw_cutoff).delete()
    deleted_alerts,   _ = DeviceAlert.objects.filter(
        is_resolved=True, resolved_at__lt=alert_cutoff
    ).delete()

    logger.info(
        f"🧹 Data Retention: {deleted_readings} SensorReading "
        f"و {deleted_alerts} DeviceAlert قدیمی پاک شدند."
    )
    return {
        'deleted_readings': deleted_readings,
        'deleted_alerts': deleted_alerts,
    }
