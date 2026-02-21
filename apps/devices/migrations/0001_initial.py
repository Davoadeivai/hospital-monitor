from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('floor', models.IntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('device_type', models.CharField(choices=[('autoclave','اتوکلاو'),('incinerator','زباله‌سوز')], max_length=20)),
                ('serial_number', models.CharField(max_length=50, unique=True)),
                ('model_number', models.CharField(blank=True, max_length=100)),
                ('manufacturer', models.CharField(blank=True, max_length=100)),
                ('capacity_kg', models.FloatField(default=10)),
                ('power_kw', models.FloatField(default=15)),
                ('steam_pressure_bar', models.FloatField(null=True, blank=True)),
                ('chamber_volume_liter', models.FloatField(null=True, blank=True)),
                ('connection_type', models.CharField(choices=[('sim','شبیه‌ساز'),('rtu','Modbus RTU'),('tcp','Modbus TCP')], default='sim', max_length=10)),
                ('plc_ip', models.GenericIPAddressField(null=True, blank=True)),
                ('plc_port', models.IntegerField(default=502)),
                ('modbus_slave_id', models.IntegerField(default=1)),
                ('serial_port', models.CharField(default='/dev/ttyUSB0', max_length=50)),
                ('baud_rate', models.IntegerField(default=9600)),
                ('polling_interval', models.IntegerField(default=5)),
                ('status', models.CharField(choices=[('online','آنلاین'),('offline','آفلاین'),('error','خطا'),('maintenance','در سرویس')], default='offline', max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('installed_at', models.DateField(null=True, blank=True)),
                ('last_seen', models.DateTimeField(null=True, blank=True)),
                ('next_maintenance', models.DateField(null=True, blank=True)),
                ('mqtt_topic', models.CharField(blank=True, max_length=200)),
                ('department', models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.SET_NULL, to='devices.department')),
            ],
        ),
        migrations.CreateModel(
            name='DeviceCycle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True)),
                ('cycle_number', models.IntegerField()),
                ('status', models.CharField(choices=[('idle','آماده'),('heating','گرمایش'),('sterilizing','استریل'),('cooling','سردسازی'),('complete','تکمیل'),('error','خطا'),('aborted','لغو شده')], default='heating', max_length=20)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField(null=True, blank=True)),
                ('waste_weight_kg', models.FloatField(default=0)),
                ('waste_type', models.CharField(choices=[('infectious','عفونی'),('sharp','تیز و برنده'),('pharmaceutical','دارویی'),('pathological','پاتولوژیک'),('chemical','شیمیایی'),('general','عمومی')], default='infectious', max_length=50)),
                ('notes', models.TextField(blank=True)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cycles', to='devices.device')),
                ('operator', models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.user')),
            ],
            options={'ordering': ['-start_time']},
        ),
        migrations.CreateModel(
            name='MaintenanceLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True)),
                ('date', models.DateField()),
                ('type', models.CharField(choices=[('PM','پیشگیرانه'),('CM','اصلاحی'),('inspection','بازرسی')], max_length=20)),
                ('description', models.TextField()),
                ('cost', models.DecimalField(decimal_places=0, default=0, max_digits=12)),
                ('technician', models.CharField(blank=True, max_length=100)),
                ('next_due', models.DateField(null=True, blank=True)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='maintenance_logs', to='devices.device')),
            ],
            options={'ordering': ['-date']},
        ),
    ]
