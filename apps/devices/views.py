from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Device, DeviceCycle, Department, MaintenanceLog


@login_required
def device_list(request):
    device_type = request.GET.get('type', '')
    devices = Device.objects.filter(is_active=True).select_related('department')
    if device_type:
        devices = devices.filter(device_type=device_type)
    return render(request, 'devices/device_list.html', {
        'devices': devices,
        'device_type_filter': device_type,
        'title': 'لیست دستگاه‌ها',
    })


@login_required
def device_detail(request, pk):
    device = get_object_or_404(Device, pk=pk)
    maintenance_logs = MaintenanceLog.objects.filter(device=device).order_by('-date')[:10]
    return render(request, 'devices/device_detail.html', {
        'device': device,
        'maintenance_logs': maintenance_logs,
        'title': device.name,
    })


@login_required
def maintenance_log(request):
    logs = MaintenanceLog.objects.select_related('device').order_by('-date')[:50]
    return render(request, 'devices/maintenance_log.html', {
        'logs': logs,
        'title': 'لاگ سرویس',
    })


@login_required
def plc_config(request, device_id):
    device = get_object_or_404(Device, pk=device_id)
    if request.method == 'POST':
        fields = ['connection_type','plc_ip','plc_port','modbus_slave_id',
                  'serial_port','baud_rate','polling_interval']
        for field in fields:
            val = request.POST.get(field)
            if val is not None and val != '':
                setattr(device, field, val)
        device.save()
        from django.contrib import messages
        messages.success(request, 'تنظیمات PLC ذخیره شد ✅')
        return redirect('plc_config', device_id=device_id)
    return render(request, 'devices/plc_config.html', {
        'device': device,
        'title': f'تنظیم PLC — {device.name}',
    })


@login_required
def plc_test(request, device_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    device = get_object_or_404(Device, pk=device_id)
    try:
        from core.plc_driver import get_plc_driver
        driver = get_plc_driver(device)
        reading = driver.read()
        if reading:
            return JsonResponse({'success': True, 'reading': reading.to_dict()})
        return JsonResponse({'success': False, 'error': 'پاسخی از PLC دریافت نشد'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
