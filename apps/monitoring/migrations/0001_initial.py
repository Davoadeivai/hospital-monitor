from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('devices', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]
    operations = [
        migrations.CreateModel(
            name='SensorReading',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(db_index=True)),
                ('temperature_c', models.FloatField(null=True, blank=True)),
                ('pressure_bar', models.FloatField(null=True, blank=True)),
                ('steam_flow_kg_h', models.FloatField(null=True, blank=True)),
                ('water_level_pct', models.FloatField(null=True, blank=True)),
                ('door_locked', models.BooleanField(null=True, blank=True)),
                ('combustion_temp_c', models.FloatField(null=True, blank=True)),
                ('exhaust_temp_c', models.FloatField(null=True, blank=True)),
                ('co_ppm', models.FloatField(null=True, blank=True)),
                ('nox_ppm', models.FloatField(null=True, blank=True)),
                ('so2_ppm', models.FloatField(null=True, blank=True)),
                ('co2_ppm', models.FloatField(null=True, blank=True)),
                ('power_consumption_kw', models.FloatField(null=True, blank=True)),
                ('device_status', models.CharField(default='idle', max_length=20)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='readings', to='devices.device')),
                ('cycle', models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.SET_NULL, related_name='readings', to='devices.devicecycle')),
            ],
            options={'ordering': ['-timestamp']},
        ),
        migrations.CreateModel(
            name='DeviceAlert',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True)),
                ('alert_type', models.CharField(choices=[('temp_high','دمای بالا'),('temp_low','دمای پایین'),('pressure_high','فشار بالا'),('pressure_low','فشار پایین'),('power','برق'),('water','آب'),('emission','آلایندگی'),('connectivity','اتصال'),('sensor','سنسور'),('other','سایر')], default='other', max_length=30)),
                ('severity', models.CharField(choices=[('info','اطلاعات'),('warning','هشدار'),('critical','بحرانی')], default='warning', max_length=10)),
                ('message', models.TextField()),
                ('value', models.CharField(blank=True, max_length=50)),
                ('threshold', models.CharField(blank=True, max_length=50)),
                ('is_resolved', models.BooleanField(default=False)),
                ('resolved_at', models.DateTimeField(null=True, blank=True)),
                ('sms_sent', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='alerts', to='devices.device')),
                ('cycle', models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.SET_NULL, to='devices.devicecycle')),
                ('resolved_by', models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.user')),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.AddIndex(
            model_name='sensorreading',
            index=models.Index(fields=['device', 'timestamp'], name='monitoring_device_ts_idx'),
        ),
    ]
