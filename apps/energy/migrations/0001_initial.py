from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [('devices', '0001_initial')]
    operations = [
        migrations.CreateModel(
            name='EnergyTariff',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True)),
                ('name', models.CharField(default='تعرفه عمومی', max_length=100)),
                ('electricity_per_kwh', models.DecimalField(decimal_places=2, default=1500, max_digits=10)),
                ('water_per_liter', models.DecimalField(decimal_places=2, default=50, max_digits=10)),
                ('fuel_per_liter', models.DecimalField(decimal_places=2, default=5000, max_digits=10)),
                ('effective_from', models.DateField()),
                ('effective_to', models.DateField(null=True, blank=True)),
            ],
            options={'ordering': ['-effective_from']},
        ),
        migrations.CreateModel(
            name='EnergyRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True)),
                ('electricity_kwh', models.FloatField(default=0)),
                ('electricity_cost', models.FloatField(default=0)),
                ('water_liter', models.FloatField(default=0)),
                ('water_cost', models.FloatField(default=0)),
                ('fuel_liter', models.FloatField(default=0)),
                ('fuel_cost', models.FloatField(default=0)),
                ('carbon_footprint_kg', models.FloatField(default=0)),
                ('total_cost', models.FloatField(default=0)),
                ('cost_per_kg', models.FloatField(default=0)),
                ('calculated_at', models.DateTimeField(auto_now=True)),
                ('cycle', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='energy', to='devices.devicecycle')),
            ],
        ),
        migrations.CreateModel(
            name='MonthlyEnergyReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True)),
                ('year', models.IntegerField()),
                ('month', models.IntegerField()),
                ('total_cycles', models.IntegerField(default=0)),
                ('total_kwh', models.FloatField(default=0)),
                ('total_water_liter', models.FloatField(default=0)),
                ('total_fuel_liter', models.FloatField(default=0)),
                ('total_carbon_kg', models.FloatField(default=0)),
                ('total_cost', models.FloatField(default=0)),
                ('total_waste_kg', models.FloatField(default=0)),
                ('generated_at', models.DateTimeField(auto_now=True)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='devices.device')),
            ],
            options={'ordering': ['-year', '-month'], 'unique_together': {('device', 'year', 'month')}},
        ),
    ]
