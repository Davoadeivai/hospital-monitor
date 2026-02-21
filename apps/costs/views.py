from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg


@login_required
def costs_dashboard(request):
    from django.utils import timezone
    from apps.energy.models import EnergyRecord
    now = timezone.now()

    records = EnergyRecord.objects.select_related(
        'cycle__device', 'cycle'
    ).order_by('-calculated_at')[:30]

    month_stats = EnergyRecord.objects.filter(
        cycle__start_time__year=now.year,
        cycle__start_time__month=now.month
    ).aggregate(
        month_total=Sum('total_cost'),
        month_kwh=Sum('electricity_kwh'),
        avg_cost_per_kg=Avg('cost_per_kg'),
        total_cycles=Count('id'),
    )

    return render(request, 'costs/dashboard.html', {
        'records': records,
        'month_total': month_stats['month_total'] or 0,
        'month_kwh': month_stats['month_kwh'] or 0,
        'avg_cost_per_kg': month_stats['avg_cost_per_kg'] or 0,
        'total_cycles': month_stats['total_cycles'] or 0,
        'title': 'هزینه‌ها',
    })
