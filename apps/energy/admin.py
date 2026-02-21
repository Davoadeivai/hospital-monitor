from django.contrib import admin
from .models import EnergyTariff, EnergyRecord, MonthlyEnergyReport


@admin.register(EnergyTariff)
class EnergyTariffAdmin(admin.ModelAdmin):
    list_display = ['name', 'electricity_per_kwh', 'water_per_liter', 'fuel_per_liter', 'effective_from', 'effective_to']
    list_filter = ['effective_from']


@admin.register(EnergyRecord)
class EnergyRecordAdmin(admin.ModelAdmin):
    list_display = ['cycle', 'electricity_kwh', 'electricity_cost', 'water_liter', 'carbon_footprint_kg', 'total_cost', 'cost_per_kg']
    list_filter = ['cycle__device', 'cycle__waste_type']
    search_fields = ['cycle__device__name']
    readonly_fields = ['calculated_at']


@admin.register(MonthlyEnergyReport)
class MonthlyEnergyReportAdmin(admin.ModelAdmin):
    list_display = ['device', 'year', 'month', 'total_cycles', 'total_kwh', 'total_cost']
    list_filter = ['device', 'year', 'month']
