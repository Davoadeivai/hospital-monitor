from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from apps.devices.models import DeviceCycle


@login_required
def waste_list(request):
    from django.utils import timezone
    now = timezone.now()
    cycles = DeviceCycle.objects.filter(
        status='complete'
    ).select_related('device', 'operator').order_by('-start_time')[:50]

    month_cycles = DeviceCycle.objects.filter(
        status='complete',
        start_time__year=now.year,
        start_time__month=now.month
    )
    stats = month_cycles.aggregate(
        total_waste_kg=Sum('waste_weight_kg'),
        infectious_kg=Sum('waste_weight_kg', filter=__import__('django.db.models', fromlist=['Q']).Q(waste_type='infectious')),
        sharp_kg=Sum('waste_weight_kg', filter=__import__('django.db.models', fromlist=['Q']).Q(waste_type='sharp')),
    )

    return render(request, 'waste/list.html', {
        'cycles': cycles,
        'total_waste_kg': stats['total_waste_kg'] or 0,
        'infectious_kg': stats['infectious_kg'] or 0,
        'sharp_kg': stats['sharp_kg'] or 0,
        'other_kg': (stats['total_waste_kg'] or 0) - (stats['infectious_kg'] or 0) - (stats['sharp_kg'] or 0),
        'title': 'مدیریت زباله',
    })
