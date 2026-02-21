from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone


@login_required
def monthly_report(request):
    from apps.energy.models import MonthlyEnergyReport
    from apps.devices.models import Device, DeviceCycle
    from django.db.models import Sum, Count
    import datetime

    now = timezone.now()
    year = int(request.GET.get('year', now.year))
    month = int(request.GET.get('month', now.month))

    reports = MonthlyEnergyReport.objects.filter(
        year=year, month=month
    ).select_related('device')

    # اگه گزارش از قبل نیست، live حساب کن
    if not reports.exists():
        devices = Device.objects.filter(is_active=True)
        live_reports = []
        for dev in devices:
            from apps.energy.models import EnergyRecord
            s = EnergyRecord.objects.filter(
                cycle__device=dev,
                cycle__start_time__year=year,
                cycle__start_time__month=month,
            ).aggregate(
                total_cycles=Count('id'),
                total_kwh=Sum('electricity_kwh'),
                total_water=Sum('water_liter'),
                total_fuel=Sum('fuel_liter'),
                total_carbon=Sum('carbon_footprint_kg'),
                total_cost=Sum('total_cost'),
            )
            total_waste = DeviceCycle.objects.filter(
                device=dev,
                start_time__year=year,
                start_time__month=month,
                status='complete',
            ).aggregate(w=Sum('waste_weight_kg'))['w'] or 0

            class R:
                pass
            r = R()
            r.device = dev
            r.year = year
            r.month = month
            r.total_cycles = s['total_cycles'] or 0
            r.total_kwh = round(s['total_kwh'] or 0, 1)
            r.total_water_liter = round(s['total_water'] or 0, 0)
            r.total_fuel_liter = round(s['total_fuel'] or 0, 0)
            r.total_carbon_kg = round(s['total_carbon'] or 0, 1)
            r.total_cost = round(s['total_cost'] or 0, 0)
            r.total_waste_kg = round(total_waste, 1)
            live_reports.append(r)
        reports = live_reports

    return render(request, 'reports/monthly.html', {
        'reports': reports,
        'year': year,
        'month': month,
        'title': 'گزارش ماهانه',
    })


@login_required
def export_excel(request):
    try:
        import openpyxl
        from apps.energy.models import EnergyRecord
        now = timezone.now()

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "گزارش هزینه"

        headers = ['دستگاه', 'شماره سیکل', 'تاریخ', 'نوع زباله', 'وزن (kg)',
                   'برق (kWh)', 'هزینه برق', 'آب (L)', 'هزینه آب', 'کربن (kg)', 'هزینه کل']
        ws.append(headers)

        records = EnergyRecord.objects.select_related(
            'cycle__device'
        ).filter(
            cycle__start_time__year=now.year,
        ).order_by('-cycle__start_time')

        for r in records:
            ws.append([
                r.cycle.device.name,
                r.cycle.cycle_number,
                str(r.cycle.start_time.date()),
                r.cycle.get_waste_type_display(),
                r.cycle.waste_weight_kg,
                round(r.electricity_kwh, 2),
                round(r.electricity_cost, 0),
                round(r.water_liter, 0),
                round(r.water_cost, 0),
                round(r.carbon_footprint_kg, 2),
                round(r.total_cost, 0),
            ])

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename=report_{now.strftime("%Y%m%d")}.xlsx'
        wb.save(response)
        return response

    except Exception as e:
        return HttpResponse(f"خطا: {e}", status=500)
