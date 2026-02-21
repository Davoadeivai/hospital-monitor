import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta

from apps.devices.models import Device, DeviceCycle, Department
from apps.monitoring.models import SensorReading, DeviceAlert
from apps.energy.models import EnergyRecord
from core.calculators import WasteStatistics


@login_required
def dashboard(request):
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = now.replace(day=1, hour=0, minute=0, second=0)

    devices = Device.objects.filter(is_active=True).select_related('department')
    total_devices = devices.count()
    online_devices = devices.filter(status='online').count()
    error_devices = devices.filter(status='error').count()
    online_pct = int((online_devices / total_devices * 100) if total_devices else 0)

    today_cycles = DeviceCycle.objects.filter(start_time__gte=today_start, status='complete')
    today_cycles_count = today_cycles.count()
    today_waste_kg = today_cycles.aggregate(total=Sum('waste_weight_kg'))['total'] or 0

    month_energy = EnergyRecord.objects.filter(
        cycle__start_time__gte=month_start, cycle__status='complete'
    ).aggregate(total_cost=Sum('total_cost'), total_kwh=Sum('electricity_kwh'),
                total_carbon=Sum('carbon_footprint_kg'), total_water=Sum('water_liter'))
    month_cost = float(month_energy['total_cost'] or 0)
    month_kwh = float(month_energy['total_kwh'] or 0)
    month_carbon = float(month_energy['total_carbon'] or 0)
    month_water = float(month_energy['total_water'] or 0)

    active_alerts = DeviceAlert.objects.filter(is_resolved=False).select_related('device').order_by('-created_at')[:10]
    critical_alerts = DeviceAlert.objects.filter(is_resolved=False, severity='critical').count()

    devices_data = []
    for device in devices:
        last_reading = SensorReading.objects.filter(device=device).order_by('-timestamp').first()
        active_cycle = DeviceCycle.objects.filter(device=device, status__in=['heating','sterilizing','cooling']).first()
        devices_data.append({'device': device, 'last_reading': last_reading, 'active_cycle': active_cycle})

    # 7-day chart
    chart_data = []
    for i in range(6, -1, -1):
        day = now - timedelta(days=i)
        ds = day.replace(hour=0, minute=0, second=0, microsecond=0)
        de = day.replace(hour=23, minute=59, second=59)
        dc = DeviceCycle.objects.filter(start_time__range=[ds, de], status='complete')
        day_cost = float(EnergyRecord.objects.filter(cycle__in=dc).aggregate(total=Sum('total_cost'))['total'] or 0)
        chart_data.append({
            'date': day.strftime('%m/%d'),
            'cycles': dc.count(),
            'cost': day_cost,
            'waste_kg': float(dc.aggregate(total=Sum('waste_weight_kg'))['total'] or 0),
        })

    # 30-day energy data
    energy_data = []
    for i in range(29, -1, -1):
        day = now - timedelta(days=i)
        ds = day.replace(hour=0, minute=0, second=0, microsecond=0)
        de = day.replace(hour=23, minute=59, second=59)
        agg = EnergyRecord.objects.filter(cycle__start_time__range=[ds, de]).aggregate(
            kwh=Sum('electricity_kwh'), cost=Sum('total_cost'))
        energy_data.append({'date': day.strftime('%m/%d'), 'kwh': round(float(agg['kwh'] or 0), 1), 'cost': float(agg['cost'] or 0)})

    # Carbon ring (% of monthly budget, assume 500kg budget)
    carbon_budget = 500
    carbon_pct = min(month_carbon / carbon_budget, 1)
    carbon_ring_offset = 377 * (1 - carbon_pct)

    context = {
        'total_devices': total_devices, 'online_devices': online_devices,
        'error_devices': error_devices, 'online_pct': online_pct,
        'today_cycles': today_cycles_count, 'today_waste_kg': round(today_waste_kg, 1),
        'month_cost_million': round(month_cost / 1_000_000, 1),
        'month_kwh': round(month_kwh, 0), 'month_carbon': round(month_carbon, 1),
        'month_water': round(month_water, 0),
        'carbon_ring_offset': round(carbon_ring_offset, 1),
        'active_alerts': active_alerts, 'critical_alerts': critical_alerts,
        'devices_data': devices_data,
        'chart_data': json.dumps(chart_data),
        'energy_data': json.dumps(energy_data),
    }
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def device_monitor(request, device_id):
    device = get_object_or_404(Device, pk=device_id, is_active=True)
    last_reading = SensorReading.objects.filter(device=device).order_by('-timestamp').first()
    active_cycle = DeviceCycle.objects.filter(
        device=device, status__in=['heating', 'sterilizing', 'cooling']
    ).order_by('-start_time').first()

    recent_readings = list(SensorReading.objects.filter(device=device).order_by('-timestamp')[:120].values(
        'timestamp', 'temperature_c', 'pressure_bar', 'power_consumption_kw',
        'combustion_temp_c', 'co_ppm', 'nox_ppm', 'so2_ppm', 'co2_ppm',
        'exhaust_temp_c', 'water_level_pct', 'device_status'
    ))
    for r in recent_readings:
        r['timestamp'] = r['timestamp'].isoformat()
    recent_readings.reverse()

    device_alerts = DeviceAlert.objects.filter(device=device, is_resolved=False).order_by('-created_at')[:5]
    stats = WasteStatistics.get_device_stats(device, days=30)
    recent_cycles = DeviceCycle.objects.filter(device=device).select_related('operator').order_by('-start_time')[:10]

    context = {
        'device': device, 'last_reading': last_reading, 'active_cycle': active_cycle,
        'recent_readings': json.dumps(recent_readings),
        'device_alerts': device_alerts, 'stats': stats, 'recent_cycles': recent_cycles,
    }
    return render(request, 'monitoring/device_monitor.html', context)


@login_required
def api_device_readings(request, device_id):
    device = get_object_or_404(Device, pk=device_id)
    minutes = int(request.GET.get('minutes', 30))
    since = timezone.now() - timedelta(minutes=minutes)
    readings = SensorReading.objects.filter(device=device, timestamp__gte=since).order_by('timestamp').values(
        'timestamp', 'temperature_c', 'pressure_bar', 'power_consumption_kw',
        'combustion_temp_c', 'co_ppm', 'nox_ppm', 'device_status')
    data = [{**r, 'timestamp': r['timestamp'].isoformat()} for r in readings]
    return JsonResponse({'readings': data, 'count': len(data)})


@login_required
def api_dashboard_stats(request):
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return JsonResponse({
        'online_devices': Device.objects.filter(is_active=True, status='online').count(),
        'today_cycles': DeviceCycle.objects.filter(start_time__gte=today_start, status='complete').count(),
        'critical_alerts': DeviceAlert.objects.filter(is_resolved=False, severity='critical').count(),
        'timestamp': now.isoformat(),
    })


@login_required
def resolve_alert(request, alert_id):
    if request.method == 'POST':
        alert = get_object_or_404(DeviceAlert, pk=alert_id)
        alert.is_resolved = True
        alert.resolved_at = timezone.now()
        alert.resolved_by = request.user
        alert.save()
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def start_cycle(request, device_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    device = get_object_or_404(Device, pk=device_id)
    if DeviceCycle.objects.filter(device=device, status__in=['heating','sterilizing','cooling']).exists():
        return JsonResponse({'error': 'دستگاه در حال کار است'}, status=400)
    last_cycle = DeviceCycle.objects.filter(device=device).order_by('-cycle_number').first()
    next_number = (last_cycle.cycle_number + 1) if last_cycle else 1
    cycle = DeviceCycle.objects.create(
        device=device, cycle_number=next_number, status='heating',
        start_time=timezone.now(),
        waste_weight_kg=float(request.POST.get('waste_weight', 0)),
        waste_type=request.POST.get('waste_type', 'infectious'),
        operator=request.user, notes=request.POST.get('notes', ''),
    )
    return JsonResponse({'success': True, 'cycle_id': cycle.pk, 'cycle_number': cycle.cycle_number})


@login_required
def complete_cycle(request, cycle_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    cycle = get_object_or_404(DeviceCycle, pk=cycle_id)
    cycle.status = 'complete'
    cycle.end_time = timezone.now()
    cycle.save()
    from apps.monitoring.tasks import calculate_cycle_energy_task
    calculate_cycle_energy_task.delay(cycle.pk)
    return JsonResponse({'success': True, 'duration_min': cycle.duration_minutes})
