from django.db import models
from django.contrib.auth.models import User
from apps.devices.models import Device, DeviceCycle


class SensorReading(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='readings')
    cycle = models.ForeignKey(DeviceCycle, on_delete=models.SET_NULL, null=True, blank=True, related_name='readings')
    timestamp = models.DateTimeField(db_index=True)

    # اتوکلاو
    temperature_c = models.FloatField(null=True, blank=True)
    pressure_bar = models.FloatField(null=True, blank=True)
    steam_flow_kg_h = models.FloatField(null=True, blank=True)
    water_level_pct = models.FloatField(null=True, blank=True)
    door_locked = models.BooleanField(null=True, blank=True)

    # زباله‌سوز
    combustion_temp_c = models.FloatField(null=True, blank=True)
    exhaust_temp_c = models.FloatField(null=True, blank=True)
    co_ppm = models.FloatField(null=True, blank=True)
    nox_ppm = models.FloatField(null=True, blank=True)
    so2_ppm = models.FloatField(null=True, blank=True)
    co2_ppm = models.FloatField(null=True, blank=True)

    # مشترک
    power_consumption_kw = models.FloatField(null=True, blank=True)
    device_status = models.CharField(max_length=20, default='idle')

    class Meta:
        ordering = ['-timestamp']
        indexes = [models.Index(fields=['device', 'timestamp'])]

    def __str__(self):
        return f"{self.device.name} @ {self.timestamp}"


class DeviceAlert(models.Model):
    SEVERITY = [('info','اطلاعات'),('warning','هشدار'),('critical','بحرانی')]
    ALERT_TYPES = [
        ('temp_high','دمای بالا'),('temp_low','دمای پایین'),
        ('pressure_high','فشار بالا'),('pressure_low','فشار پایین'),
        ('power','برق'),('water','آب'),('emission','آلایندگی'),
        ('connectivity','اتصال'),('sensor','سنسور'),('other','سایر'),
    ]

    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='alerts')
    cycle = models.ForeignKey(DeviceCycle, on_delete=models.SET_NULL, null=True, blank=True)
    alert_type = models.CharField(max_length=30, choices=ALERT_TYPES, default='other')
    severity = models.CharField(max_length=10, choices=SEVERITY, default='warning')
    message = models.TextField()
    value = models.CharField(max_length=50, blank=True)
    threshold = models.CharField(max_length=50, blank=True)
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    sms_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.severity}] {self.device.name}: {self.message[:50]}"

    def get_severity_display(self):
        return dict(self.SEVERITY).get(self.severity, self.severity)

    def get_alert_type_display(self):
        return dict(self.ALERT_TYPES).get(self.alert_type, self.alert_type)
