from django.db import models
from django.contrib.auth.models import User


class Department(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام بخش")
    floor = models.IntegerField(default=1, verbose_name="طبقه")
    class Meta:
        verbose_name = "بخش"; verbose_name_plural = "بخش‌ها"
    def __str__(self): return self.name


class Device(models.Model):
    DEVICE_TYPES = [('autoclave', 'اتوکلاو'), ('incinerator', 'زباله‌سوز')]
    STATUS_CHOICES = [('online', 'آنلاین'), ('offline', 'آفلاین'), ('error', 'خطا'), ('maintenance', 'در سرویس')]
    CONNECTION_TYPES = [('sim', 'شبیه‌ساز (تست)'), ('rtu', 'Modbus RTU — RS485'), ('tcp', 'Modbus TCP — Ethernet')]

    # اطلاعات پایه
    name = models.CharField(max_length=100, verbose_name="نام دستگاه")
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPES, verbose_name="نوع")
    serial_number = models.CharField(max_length=50, unique=True, verbose_name="سریال")
    model_number = models.CharField(max_length=100, blank=True, verbose_name="مدل")
    manufacturer = models.CharField(max_length=100, blank=True, verbose_name="سازنده")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="بخش")

    # مشخصات فنی
    capacity_kg = models.FloatField(verbose_name="ظرفیت (kg)", default=10)
    power_kw = models.FloatField(verbose_name="توان (kW)", default=15)
    steam_pressure_bar = models.FloatField(null=True, blank=True, verbose_name="فشار بخار (bar)")
    chamber_volume_liter = models.FloatField(null=True, blank=True, verbose_name="حجم محفظه (L)")

    # اتصال PLC COTRUST
    connection_type = models.CharField(max_length=10, choices=CONNECTION_TYPES, default='sim', verbose_name="نوع اتصال")
    plc_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name="آدرس IP پی‌ال‌سی")
    plc_port = models.IntegerField(default=502, verbose_name="پورت Modbus TCP")
    modbus_slave_id = models.IntegerField(default=1, verbose_name="Slave ID")
    serial_port = models.CharField(max_length=50, default="/dev/ttyUSB0", verbose_name="پورت سریال (RS485)")
    baud_rate = models.IntegerField(default=9600, verbose_name="Baud Rate")
    polling_interval = models.IntegerField(default=5, verbose_name="فاصله polling (ثانیه)")

    # وضعیت
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='offline', verbose_name="وضعیت")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    installed_at = models.DateField(null=True, blank=True, verbose_name="تاریخ نصب")
    last_seen = models.DateTimeField(null=True, blank=True, verbose_name="آخرین اتصال")
    next_maintenance = models.DateField(null=True, blank=True, verbose_name="سرویس بعدی")
    mqtt_topic = models.CharField(max_length=200, blank=True, verbose_name="MQTT Topic")

    class Meta:
        verbose_name = "دستگاه"; verbose_name_plural = "دستگاه‌ها"

    def __str__(self):
        return f"{self.name} ({self.serial_number})"

    @property
    def maintenance_due(self):
        if self.next_maintenance:
            from django.utils import timezone
            return self.next_maintenance <= timezone.now().date()
        return False

    @property
    def is_plc_connected(self):
        return self.connection_type != 'sim'

    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

    def get_device_type_display(self):
        return dict(self.DEVICE_TYPES).get(self.device_type, self.device_type)


class DeviceCycle(models.Model):
    STATUS_CHOICES = [
        ('idle', 'آماده'), ('heating', 'گرمایش'), ('sterilizing', 'استریل'),
        ('cooling', 'سردسازی'), ('complete', 'تکمیل'), ('error', 'خطا'), ('aborted', 'لغو شده'),
    ]
    WASTE_TYPES = [
        ('infectious', 'عفونی'), ('sharp', 'تیز و برنده'), ('pharmaceutical', 'دارویی'),
        ('pathological', 'پاتولوژیک'), ('chemical', 'شیمیایی'), ('general', 'عمومی'),
    ]

    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='cycles')
    cycle_number = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='heating')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    waste_weight_kg = models.FloatField(default=0)
    waste_type = models.CharField(max_length=50, choices=WASTE_TYPES, default='infectious')
    operator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "سیکل"; verbose_name_plural = "سیکل‌ها"; ordering = ['-start_time']

    def __str__(self):
        return f"سیکل #{self.cycle_number} — {self.device.name}"

    @property
    def duration_minutes(self):
        if self.end_time and self.start_time:
            return int((self.end_time - self.start_time).total_seconds() / 60)
        return None

    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

    def get_waste_type_display(self):
        return dict(self.WASTE_TYPES).get(self.waste_type, self.waste_type)


class MaintenanceLog(models.Model):
    TYPES = [('PM', 'پیشگیرانه'), ('CM', 'اصلاحی'), ('inspection', 'بازرسی')]
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='maintenance_logs')
    date = models.DateField()
    type = models.CharField(max_length=20, choices=TYPES)
    description = models.TextField()
    cost = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    technician = models.CharField(max_length=100, blank=True)
    next_due = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "لاگ سرویس"; verbose_name_plural = "لاگ‌های سرویس"; ordering = ['-date']

    def __str__(self):
        return f"{self.device.name} — {self.date}"
