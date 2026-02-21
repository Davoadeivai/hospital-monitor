"""
python manage.py setup_demo

ایجاد داده‌های نمونه واقع‌گرایانه برای تست پروژه
شامل دستگاه‌ها، سیکل‌ها، داده‌های سنسور، هشدارها و گزارش‌ها
"""
import random
import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone


class Command(BaseCommand):
    help = 'ایجاد داده‌های نمونه برای تست'

    def handle(self, *args, **options):
        self.stdout.write('\n🏥 در حال ساخت داده‌های نمونه...\n')

        # ── ۱. کاربر ادمین ──────────────────────────────────────
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@hospital.ir', 'admin123')
            self.stdout.write('  ✅ کاربر admin ساخته شد (رمز: admin123)')
        else:
            self.stdout.write('  ℹ️  کاربر admin از قبل وجود دارد')

        operator = User.objects.filter(username='admin').first()

        # ── ۲. بخش‌ها ────────────────────────────────────────────
        from apps.devices.models import Department, Device, DeviceCycle, MaintenanceLog
        departments = {}
        for name, floor in [('اتاق عمل', 3), ('ICU', 2), ('اورژانس', 1), ('آزمایشگاه', 1)]:
            dept, _ = Department.objects.get_or_create(name=name, defaults={'floor': floor})
            departments[name] = dept
        self.stdout.write(f'  ✅ {len(departments)} بخش ساخته شد')

        # ── ۳. دستگاه‌ها ─────────────────────────────────────────
        devices_data = [
            {
                'name': 'اتوکلاو A1 — اتاق عمل',
                'device_type': 'autoclave',
                'serial_number': 'AC-2021-001',
                'model_number': 'Tuttnauer 3870EA',
                'manufacturer': 'Tuttnauer',
                'department': departments['اتاق عمل'],
                'capacity_kg': 12.0,
                'power_kw': 18.0,
                'steam_pressure_bar': 2.1,
                'connection_type': 'sim',
                'polling_interval': 5,
            },
            {
                'name': 'اتوکلاو B2 — ICU',
                'device_type': 'autoclave',
                'serial_number': 'AC-2022-002',
                'model_number': 'MELAG 23',
                'manufacturer': 'MELAG',
                'department': departments['ICU'],
                'capacity_kg': 8.0,
                'power_kw': 12.0,
                'steam_pressure_bar': 2.0,
                'connection_type': 'sim',
                'polling_interval': 5,
            },
            {
                'name': 'زباله‌سوز C1 — پشت‌بام',
                'device_type': 'incinerator',
                'serial_number': 'IN-2020-001',
                'model_number': 'Inciner8 I8-50',
                'manufacturer': 'Inciner8',
                'department': departments['اورژانس'],
                'capacity_kg': 50.0,
                'power_kw': 45.0,
                'connection_type': 'sim',
                'polling_interval': 10,
            },
        ]

        created_devices = []
        for d in devices_data:
            dev, created = Device.objects.get_or_create(
                serial_number=d['serial_number'],
                defaults={**d, 'installed_at': datetime.date(2021, 3, 15), 'status': 'online',
                           'next_maintenance': datetime.date.today() + datetime.timedelta(days=30)}
            )
            created_devices.append(dev)
            tag = '✅' if created else 'ℹ️ '
            self.stdout.write(f'  {tag} دستگاه: {dev.name}')

        # ── ۴. تعرفه انرژی ───────────────────────────────────────
        from apps.energy.models import EnergyTariff
        tariff, _ = EnergyTariff.objects.get_or_create(
            name='تعرفه ۱۴۰۳',
            defaults={
                'electricity_per_kwh': 2800,
                'water_per_liter': 85,
                'fuel_per_liter': 6500,
                'effective_from': datetime.date(2024, 1, 1),
            }
        )
        self.stdout.write(f'  ✅ تعرفه انرژی: {tariff.name}')

        # ── ۵. سیکل‌ها و داده‌های سنسور ─────────────────────────
        from apps.monitoring.models import SensorReading, DeviceAlert
        from apps.energy.models import EnergyRecord

        total_cycles = 0
        total_readings = 0

        for device in created_devices:
            if DeviceCycle.objects.filter(device=device).count() > 5:
                self.stdout.write(f'  ℹ️  سیکل‌های {device.name} از قبل موجود است')
                continue

            num_cycles = 15 if device.device_type == 'autoclave' else 8
            for i in range(num_cycles):
                days_ago = random.randint(1, 45)
                start = timezone.now() - datetime.timedelta(
                    days=days_ago,
                    hours=random.randint(6, 18),
                    minutes=random.randint(0, 59)
                )

                duration = random.randint(25, 45) if device.device_type == 'autoclave' else random.randint(60, 180)
                end = start + datetime.timedelta(minutes=duration)

                waste_types = ['infectious', 'sharp', 'pharmaceutical', 'general']
                cycle = DeviceCycle.objects.create(
                    device=device,
                    cycle_number=1000 + total_cycles + i,
                    status='complete',
                    start_time=start,
                    end_time=end,
                    waste_weight_kg=round(random.uniform(3.0, device.capacity_kg * 0.8), 1),
                    waste_type=random.choice(waste_types),
                    operator=operator,
                )

                # داده‌های سنسور — هر ۳۰ ثانیه
                readings = []
                current = start
                temp = 25.0
                pressure = 0.0
                phase_time = 0

                while current <= end:
                    elapsed_pct = (current - start).total_seconds() / (duration * 60)

                    if elapsed_pct < 0.4:  # گرمایش
                        temp = min(121.5, 25 + elapsed_pct * 240)
                        pressure = min(2.1, elapsed_pct * 5.25)
                        power = 18.0 + random.uniform(-0.5, 0.5)
                        status = 'heating'
                    elif elapsed_pct < 0.7:  # استریل
                        temp = 121.5 + random.uniform(-0.3, 0.3)
                        pressure = 2.1 + random.uniform(-0.05, 0.05)
                        power = 8.0 + random.uniform(-0.3, 0.3)
                        status = 'sterilizing'
                    else:  # سردسازی
                        remaining = (1 - elapsed_pct) / 0.3
                        temp = max(40.0, 121.5 * remaining)
                        pressure = max(0.0, 2.1 * remaining)
                        power = 0.5 + random.uniform(0, 0.2)
                        status = 'cooling'

                    if device.device_type == 'autoclave':
                        readings.append(SensorReading(
                            device=device, cycle=cycle, timestamp=current,
                            temperature_c=round(temp, 1),
                            pressure_bar=round(pressure, 2),
                            steam_flow_kg_h=round(8.2 + random.uniform(-0.5, 0.5), 1) if status == 'sterilizing' else 0.0,
                            water_level_pct=round(74 + random.uniform(-3, 3), 0),
                            power_consumption_kw=round(power, 1),
                            device_status=status,
                        ))
                    else:
                        readings.append(SensorReading(
                            device=device, cycle=cycle, timestamp=current,
                            combustion_temp_c=round(850 + random.uniform(-20, 20), 0),
                            exhaust_temp_c=round(250 + random.uniform(-15, 15), 0),
                            co2_ppm=round(12.5 + random.uniform(-1, 1), 1),
                            co_ppm=round(45 + random.uniform(-5, 5), 0),
                            power_consumption_kw=round(power * 2.5, 1),
                            device_status=status,
                        ))
                    current += datetime.timedelta(seconds=30)

                SensorReading.objects.bulk_create(readings, batch_size=500)
                total_readings += len(readings)

                # محاسبه انرژی
                kwh = round(device.power_kw * duration / 60 * random.uniform(0.7, 0.95), 2)
                water = round(random.uniform(8, 15) if device.device_type == 'autoclave' else 0, 1)
                fuel = round(random.uniform(2, 5) if device.device_type == 'incinerator' else 0, 1)
                carbon = round(kwh * 0.592, 2)
                elec_cost = kwh * float(tariff.electricity_per_kwh)
                water_cost = water * float(tariff.water_per_liter)
                fuel_cost = fuel * float(tariff.fuel_per_liter)
                total_cost = elec_cost + water_cost + fuel_cost
                cost_per_kg = total_cost / cycle.waste_weight_kg if cycle.waste_weight_kg > 0 else 0

                EnergyRecord.objects.create(
                    cycle=cycle,
                    electricity_kwh=kwh,
                    electricity_cost=round(elec_cost, 0),
                    water_liter=water,
                    water_cost=round(water_cost, 0),
                    fuel_liter=fuel,
                    fuel_cost=round(fuel_cost, 0),
                    carbon_footprint_kg=carbon,
                    total_cost=round(total_cost, 0),
                    cost_per_kg=round(cost_per_kg, 0),
                )

            total_cycles += num_cycles
            self.stdout.write(f'  ✅ {device.name}: {num_cycles} سیکل')

        # ── ۶. هشدارهای نمونه ────────────────────────────────────
        if DeviceAlert.objects.count() < 5:
            alert_samples = [
                {'device': created_devices[0], 'alert_type': 'temp_high', 'severity': 'warning',
                 'message': 'دمای دستگاه از ۱۲۵°C بیشتر شد', 'value': '125.8', 'threshold': '125'},
                {'device': created_devices[0], 'alert_type': 'pressure_low', 'severity': 'warning',
                 'message': 'فشار بخار کمتر از حد مجاز', 'value': '1.4', 'threshold': '1.5'},
                {'device': created_devices[2], 'alert_type': 'emission', 'severity': 'critical',
                 'message': 'غلظت CO بالاتر از استاندارد محیط زیست', 'value': '180', 'threshold': '150'},
            ]
            for a in alert_samples:
                DeviceAlert.objects.create(**a, cycle=None, created_at=timezone.now() - datetime.timedelta(hours=random.randint(1, 24)))
            self.stdout.write(f'  ✅ {len(alert_samples)} هشدار نمونه ساخته شد')

        # ── ۷. لاگ سرویس ─────────────────────────────────────────
        if MaintenanceLog.objects.count() < 3:
            for dev in created_devices[:2]:
                MaintenanceLog.objects.create(
                    device=dev, date=datetime.date.today() - datetime.timedelta(days=30),
                    type='PM', description='سرویس دوره‌ای ۳ ماهه — تعویض واشر و بررسی سیستم بخار',
                    cost=2500000, technician='مهندس رضایی',
                    next_due=datetime.date.today() + datetime.timedelta(days=60),
                )
            self.stdout.write('  ✅ لاگ سرویس ساخته شد')

        # ── خلاصه ────────────────────────────────────────────────
        self.stdout.write(f'''
╔══════════════════════════════════════════╗
║   ✅  داده‌های نمونه با موفقیت ساخته شد  ║
╠══════════════════════════════════════════╣
║  🔬 دستگاه‌ها:   {Device.objects.count():>4}                         ║
║  🔄 سیکل‌ها:     {DeviceCycle.objects.count():>4}                         ║
║  📊 Readings:   {SensorReading.objects.count():>4}                         ║
║  ⚡ انرژی:      {EnergyRecord.objects.count():>4}                         ║
║  🚨 هشدارها:    {DeviceAlert.objects.count():>4}                         ║
╠══════════════════════════════════════════╣
║  🌐 آدرس:  http://localhost:8000         ║
║  👤 کاربر: admin  |  رمز: admin123       ║
╚══════════════════════════════════════════╝
''')
