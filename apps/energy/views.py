from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Avg, Count
from django.utils import timezone


@login_required
def energy_dashboard(request):
    from apps.energy.models import EnergyRecord, EnergyTariff, MonthlyEnergyReport
    from apps.devices.models import Device
    import json

    now = timezone.now()

    # ماه جاری
    month_stats = EnergyRecord.objects.filter(
        cycle__start_time__year=now.year,
        cycle__start_time__month=now.month
    ).aggregate(
        total_kwh=Sum('electricity_kwh'),
        total_water=Sum('water_liter'),
        total_fuel=Sum('fuel_liter'),
        total_carbon=Sum('carbon_footprint_kg'),
        total_cost=Sum('total_cost'),
    )

    # آمار ماه‌های اخیر برای نمودار
    monthly_data = []
    for i in range(11, -1, -1):
        import datetime
        d = now - datetime.timedelta(days=i*30)
        m_stats = EnergyRecord.objects.filter(
            cycle__start_time__year=d.year,
            cycle__start_time__month=d.month
        ).aggregate(kwh=Sum('electricity_kwh'), cost=Sum('total_cost'))
        monthly_data.append({
            'month': f"{d.year}/{d.month:02d}",
            'kwh': round(m_stats['kwh'] or 0, 1),
            'cost': round(m_stats['cost'] or 0, 0),
        })

    # آمار هر دستگاه
    devices = Device.objects.filter(is_active=True)
    device_stats = []
    for dev in devices:
        s = EnergyRecord.objects.filter(
            cycle__device=dev,
            cycle__start_time__year=now.year,
            cycle__start_time__month=now.month,
        ).aggregate(
            kwh=Sum('electricity_kwh'),
            water=Sum('water_liter'),
            fuel=Sum('fuel_liter'),
            carbon=Sum('carbon_footprint_kg'),
            cost=Sum('total_cost'),
            cycles=Count('id'),
        )
        device_stats.append({'device': dev, **{k: round(v or 0, 1) for k, v in s.items()}})

    return render(request, 'energy/dashboard.html', {
        'month_stats': month_stats,
        'monthly_data_json': json.dumps(monthly_data),
        'device_stats': device_stats,
        'device_names_json': json.dumps([d['device'].name for d in device_stats]),
        'device_kwh_json': json.dumps([d['kwh'] for d in device_stats]),
        'title': 'انرژی',
    })


@login_required
def tariff_list(request):
    from apps.energy.models import EnergyTariff
    tariffs = EnergyTariff.objects.all()
    return render(request, 'energy/tariff_list.html', {'tariffs': tariffs, 'title': 'تعرفه‌ها'})
