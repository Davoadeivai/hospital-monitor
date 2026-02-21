from django.contrib import admin
from django.utils.html import format_html
from .models import Device, DeviceCycle, Department, MaintenanceLog


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'floor']
    search_fields = ['name']


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['name', 'device_type', 'serial_number', 'department',
                    'connection_type', 'status_badge', 'last_seen']
    list_filter = ['device_type', 'status', 'connection_type', 'is_active']
    search_fields = ['name', 'serial_number', 'manufacturer']
    readonly_fields = ['last_seen', 'status']

    fieldsets = (
        ('اطلاعات پایه', {
            'fields': ('name', 'device_type', 'serial_number', 'model_number', 'manufacturer', 'department')
        }),
        ('مشخصات فنی', {
            'fields': ('capacity_kg', 'power_kw', 'steam_pressure_bar', 'chamber_volume_liter')
        }),
        ('اتصال PLC', {
            'fields': ('connection_type', 'plc_ip', 'plc_port', 'modbus_slave_id',
                       'serial_port', 'baud_rate', 'polling_interval'),
            'classes': ('collapse',),
        }),
        ('وضعیت', {
            'fields': ('status', 'is_active', 'installed_at', 'last_seen', 'next_maintenance')
        }),
    )

    def status_badge(self, obj):
        colors = {'online': '#00ff88', 'offline': '#555', 'error': '#ff2244', 'maintenance': '#ffb800'}
        color = colors.get(obj.status, '#555')
        return format_html(
            '<span style="background:{};color:#000;padding:2px 8px;border-radius:12px;font-size:11px;font-weight:700">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'وضعیت'


@admin.register(DeviceCycle)
class DeviceCycleAdmin(admin.ModelAdmin):
    list_display = ['device', 'cycle_number', 'status', 'start_time', 'waste_weight_kg', 'waste_type', 'operator']
    list_filter = ['status', 'waste_type', 'device']
    search_fields = ['device__name', 'cycle_number']
    date_hierarchy = 'start_time'
    readonly_fields = ['start_time']


@admin.register(MaintenanceLog)
class MaintenanceLogAdmin(admin.ModelAdmin):
    list_display = ['device', 'type', 'date', 'technician', 'cost', 'next_due']
    list_filter = ['type', 'device']
    search_fields = ['device__name', 'description', 'technician']
    date_hierarchy = 'date'
