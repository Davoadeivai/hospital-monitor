from django.db import models
from apps.devices.models import DeviceCycle


class EnergyTariff(models.Model):
    name = models.CharField(max_length=100, default='تعرفه عمومی')
    electricity_per_kwh = models.DecimalField(max_digits=10, decimal_places=2, default=1500)
    water_per_liter = models.DecimalField(max_digits=10, decimal_places=2, default=50)
    fuel_per_liter = models.DecimalField(max_digits=10, decimal_places=2, default=5000)
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-effective_from']

    def __str__(self):
        return f"{self.name} از {self.effective_from}"


class EnergyRecord(models.Model):
    cycle = models.OneToOneField(DeviceCycle, on_delete=models.CASCADE, related_name='energy')
    electricity_kwh = models.FloatField(default=0)
    electricity_cost = models.FloatField(default=0)
    water_liter = models.FloatField(default=0)
    water_cost = models.FloatField(default=0)
    fuel_liter = models.FloatField(default=0)
    fuel_cost = models.FloatField(default=0)
    carbon_footprint_kg = models.FloatField(default=0)
    total_cost = models.FloatField(default=0)
    cost_per_kg = models.FloatField(default=0)
    calculated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"انرژی سیکل #{self.cycle.cycle_number} — {self.cycle.device.name}"


class MonthlyEnergyReport(models.Model):
    device = models.ForeignKey('devices.Device', on_delete=models.CASCADE)
    year = models.IntegerField()
    month = models.IntegerField()
    total_cycles = models.IntegerField(default=0)
    total_kwh = models.FloatField(default=0)
    total_water_liter = models.FloatField(default=0)
    total_fuel_liter = models.FloatField(default=0)
    total_carbon_kg = models.FloatField(default=0)
    total_cost = models.FloatField(default=0)
    total_waste_kg = models.FloatField(default=0)
    generated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['device', 'year', 'month']
        ordering = ['-year', '-month']

    def __str__(self):
        return f"{self.device.name} — {self.year}/{self.month:02d}"
