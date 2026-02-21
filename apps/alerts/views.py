from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from apps.monitoring.models import DeviceAlert


@login_required
def alert_list(request):
    severity = request.GET.get('severity', '')
    alerts = DeviceAlert.objects.select_related('device', 'cycle').filter(is_resolved=False)
    if severity:
        alerts = alerts.filter(severity=severity)
    alerts = alerts.order_by('-created_at')[:100]

    resolved_today = DeviceAlert.objects.filter(
        is_resolved=True,
        resolved_at__date=timezone.now().date()
    ).count()

    return render(request, 'alerts/list.html', {
        'alerts': alerts,
        'severity_filter': severity,
        'critical_count': DeviceAlert.objects.filter(severity='critical', is_resolved=False).count(),
        'warning_count': DeviceAlert.objects.filter(severity='warning', is_resolved=False).count(),
        'resolved_today': resolved_today,
        'title': 'هشدارها',
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
    return JsonResponse({'success': False}, status=405)


@login_required
def resolve_all_alerts(request):
    if request.method == 'POST':
        DeviceAlert.objects.filter(is_resolved=False).update(
            is_resolved=True,
            resolved_at=timezone.now(),
        )
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=405)
