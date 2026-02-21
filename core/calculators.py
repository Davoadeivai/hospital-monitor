"""
موتور محاسبات انرژی و هزینه
Energy & Cost Calculation Engine
"""
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class EnergyCalculator:
    """محاسبه انرژی مصرفی هر سیکل"""

    CARBON_FACTOR = getattr(settings, 'CARBON_FACTOR_KG_PER_KWH', 0.592)  # ضریب کربن ایران

    @classmethod
    def calculate_cycle_energy(cls, cycle) -> dict:
        """
        محاسبه کامل انرژی یک سیکل
        Returns: dict با مقادیر انرژی و هزینه
        """
        from apps.monitoring.models import SensorReading
        from apps.energy.models import EnergyTariff

        readings = SensorReading.objects.filter(
            cycle=cycle
        ).order_by('timestamp').values_list('timestamp', 'power_consumption_kw', 'steam_flow_kg_h', 'fuel_flow_lh')

        readings = list(readings)

        if len(readings) < 2:
            return cls._empty_result()

        electricity_kwh = 0.0
        water_liter = 0.0
        fuel_liter = 0.0

        for i in range(1, len(readings)):
            t1, p1, s1, f1 = readings[i - 1]
            t2, p2, s2, f2 = readings[i]

            dt_hours = (t2 - t1).total_seconds() / 3600.0

            # برق (ذوزنقه)
            avg_power = ((p1 or 0) + (p2 or 0)) / 2
            electricity_kwh += avg_power * dt_hours

            # آب/بخار (اتوکلاو)
            if s1 is not None and s2 is not None:
                avg_steam = (s1 + s2) / 2
                water_liter += avg_steam * dt_hours * 1.0  # ۱ kg بخار ≈ ۱ لیتر آب

            # سوخت (زباله‌سوز)
            if f1 is not None and f2 is not None:
                avg_fuel = (f1 + f2) / 2
                fuel_liter += avg_fuel * dt_hours

        # دریافت تعرفه
        tariff = EnergyTariff.objects.filter(is_current=True).first()
        if not tariff:
            tariff = EnergyTariff.objects.order_by('-effective_from').first()

        if tariff:
            electricity_cost = electricity_kwh * float(tariff.electricity_per_kwh)
            water_cost = water_liter * float(tariff.water_per_liter)
            fuel_cost = fuel_liter * float(tariff.fuel_per_liter)
        else:
            electricity_cost = 0
            water_cost = 0
            fuel_cost = 0
            tariff = None

        total_cost = electricity_cost + water_cost + fuel_cost
        carbon_footprint = electricity_kwh * cls.CARBON_FACTOR

        cost_per_kg = 0
        if cycle.waste_weight_kg > 0:
            cost_per_kg = total_cost / cycle.waste_weight_kg

        return {
            'electricity_kwh': round(electricity_kwh, 3),
            'electricity_cost': round(electricity_cost, 0),
            'water_liter': round(water_liter, 2),
            'water_cost': round(water_cost, 0),
            'fuel_liter': round(fuel_liter, 2),
            'fuel_cost': round(fuel_cost, 0),
            'carbon_footprint_kg': round(carbon_footprint, 3),
            'total_cost': round(total_cost, 0),
            'cost_per_kg': round(cost_per_kg, 0),
            'tariff': tariff,
        }

    @classmethod
    def save_energy_record(cls, cycle):
        """محاسبه و ذخیره رکورد انرژی"""
        from apps.energy.models import EnergyRecord

        data = cls.calculate_cycle_energy(cycle)
        if not data:
            return None

        record, created = EnergyRecord.objects.update_or_create(
            cycle=cycle,
            defaults={
                'tariff': data.get('tariff'),
                'electricity_kwh': data['electricity_kwh'],
                'electricity_cost': data['electricity_cost'],
                'water_liter': data['water_liter'],
                'water_cost': data['water_cost'],
                'fuel_liter': data['fuel_liter'],
                'fuel_cost': data['fuel_cost'],
                'carbon_footprint_kg': data['carbon_footprint_kg'],
                'total_cost': data['total_cost'],
                'cost_per_kg': data['cost_per_kg'],
            }
        )
        return record

    @classmethod
    def _empty_result(cls):
        return {
            'electricity_kwh': 0,
            'electricity_cost': 0,
            'water_liter': 0,
            'water_cost': 0,
            'fuel_liter': 0,
            'fuel_cost': 0,
            'carbon_footprint_kg': 0,
            'total_cost': 0,
            'cost_per_kg': 0,
            'tariff': None,
        }


class AlertChecker:
    """بررسی و تولید هشدار"""

    THRESHOLDS = {
        'autoclave': {
            'temp_high': 140,
            'temp_low': 115,
            'pressure_high': 2.5,
            'pressure_low': 0.8,
            'power_high': None,  # از مشخصات دستگاه می‌گیره
        },
        'incinerator': {
            'combustion_temp_low': 850,
            'combustion_temp_high': 1200,
            'co_high': 100,  # ppm
            'nox_high': 400,  # ppm
            'so2_high': 200,  # ppm
        }
    }

    @classmethod
    def check_reading(cls, reading):
        """بررسی یک داده سنسور و تولید هشدار در صورت نیاز"""
        from apps.monitoring.models import DeviceAlert

        alerts_created = []
        device = reading.device
        device_type = device.device_type

        def create_alert(alert_type, severity, message, value, threshold):
            # بررسی نداشتن هشدار مشابه باز
            existing = DeviceAlert.objects.filter(
                device=device,
                alert_type=alert_type,
                is_resolved=False,
            ).exists()
            if not existing:
                alert = DeviceAlert.objects.create(
                    device=device,
                    cycle=reading.cycle,
                    alert_type=alert_type,
                    severity=severity,
                    message=message,
                    value=value,
                    threshold=threshold,
                )
                alerts_created.append(alert)
                return alert
            return None

        if device_type == 'autoclave':
            thresholds = cls.THRESHOLDS['autoclave']

            if reading.temperature_c is not None:
                if reading.temperature_c > thresholds['temp_high']:
                    create_alert('temp_high', 'critical',
                                 f"دمای اتوکلاو {reading.temperature_c}°C از حد {thresholds['temp_high']}°C بالاتر است!",
                                 reading.temperature_c, thresholds['temp_high'])
                elif reading.temperature_c < thresholds['temp_low'] and reading.device_status == 'sterilizing':
                    create_alert('temp_low', 'warning',
                                 f"دمای اتوکلاو {reading.temperature_c}°C از حد {thresholds['temp_low']}°C پایین‌تر است!",
                                 reading.temperature_c, thresholds['temp_low'])

            if reading.pressure_bar is not None:
                if reading.pressure_bar > thresholds['pressure_high']:
                    create_alert('pressure_high', 'critical',
                                 f"فشار {reading.pressure_bar} bar از حد مجاز {thresholds['pressure_high']} bar بیشتر است!",
                                 reading.pressure_bar, thresholds['pressure_high'])

        elif device_type == 'incinerator':
            thresholds = cls.THRESHOLDS['incinerator']

            if reading.co_ppm is not None and reading.co_ppm > thresholds['co_high']:
                create_alert('co_high', 'critical',
                             f"غلظت CO: {reading.co_ppm} ppm - بیش از حد مجاز {thresholds['co_high']} ppm!",
                             reading.co_ppm, thresholds['co_high'])

            if reading.nox_ppm is not None and reading.nox_ppm > thresholds['nox_high']:
                create_alert('nox_high', 'warning',
                             f"غلظت NOx: {reading.nox_ppm} ppm - بیش از حد مجاز {thresholds['nox_high']} ppm",
                             reading.nox_ppm, thresholds['nox_high'])

            if reading.combustion_temp_c is not None:
                if reading.combustion_temp_c < thresholds['combustion_temp_low']:
                    create_alert('temp_low', 'warning',
                                 f"دمای احتراق {reading.combustion_temp_c}°C زیر حد استاندارد {thresholds['combustion_temp_low']}°C است",
                                 reading.combustion_temp_c, thresholds['combustion_temp_low'])

        return alerts_created


class WasteStatistics:
    """آمار و تحلیل زباله"""

    @staticmethod
    def get_device_stats(device, days=30):
        """آمار ۳۰ روز اخیر یک دستگاه"""
        from django.utils import timezone
        from django.db.models import Sum, Avg, Count, F
        from apps.devices.models import DeviceCycle
        from apps.energy.models import EnergyRecord

        start_date = timezone.now() - timezone.timedelta(days=days)

        cycles = DeviceCycle.objects.filter(
            device=device,
            start_time__gte=start_date,
            status='complete'
        )

        stats = cycles.aggregate(
            total_cycles=Count('id'),
            total_waste_kg=Sum('waste_weight_kg'),
            avg_waste_kg=Avg('waste_weight_kg'),
        )

        energy_stats = EnergyRecord.objects.filter(cycle__in=cycles).aggregate(
            total_kwh=Sum('electricity_kwh'),
            total_water=Sum('water_liter'),
            total_fuel=Sum('fuel_liter'),
            total_cost=Sum('total_cost'),
            total_carbon=Sum('carbon_footprint_kg'),
        )

        return {**stats, **energy_stats}
