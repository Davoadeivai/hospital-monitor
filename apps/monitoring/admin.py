from django.contrib import admin
from django.utils.html import format_html
from .models import SensorReading, DeviceAlert


@admin.register(SensorReading)
class SensorReadingAdmin(admin.ModelAdmin):
    list_display = ['device', 'timestamp', 'temperature_c', 'pressure_bar', 'power_consumption_kw', 'device_status']
    list_filter = ['device', 'device_status']
    date_hierarchy = 'timestamp'
    readonly_fields = ['timestamp']


@admin.register(DeviceAlert)
class DeviceAlertAdmin(admin.ModelAdmin):
    list_display = ['device', 'severity_badge', 'alert_type', 'message_short', 'is_resolved', 'created_at']
    list_filter = ['severity', 'is_resolved', 'alert_type', 'device']
    search_fields = ['message', 'device__name']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']
    actions = ['mark_resolved']

    def severity_badge(self, obj):
        colors = {'critical': '#ff2244', 'warning': '#ffb800', 'info': '#00d4ff'}
        color = colors.get(obj.severity, '#555')
        return format_html(
            '<span style="background:{};color:#000;padding:2px 8px;border-radius:12px;font-size:11px;font-weight:700">{}</span>',
            color, obj.get_severity_display()
        )
    severity_badge.short_description = 'سطح'

    def message_short(self, obj):
        return obj.message[:60] + '...' if len(obj.message) > 60 else obj.message
    message_short.short_description = 'پیام'

    @admin.action(description='علامت‌گذاری به عنوان حل شده')
    def mark_resolved(self, request, queryset):
        from django.utils import timezone
        queryset.update(is_resolved=True, resolved_at=timezone.now(), resolved_by=request.user)
