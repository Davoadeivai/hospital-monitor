def global_context(request):
    """متغیرهای سراسری برای همه template ها"""
    context = {}
    if request.user.is_authenticated:
        try:
            from apps.monitoring.models import DeviceAlert
            context['unresolved_alerts_count'] = DeviceAlert.objects.filter(is_resolved=False).count()
        except Exception:
            context['unresolved_alerts_count'] = 0
    return context
