from datetime import date

from django.contrib import messages
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.scoping import scoped_buses, scoped_maintenance, scoped_maintenances
from .models import MaintenanceRecord
from apps.core.permissions import admin_required


def _parse_date(raw):
    if not raw:
        return None
    raw = raw.strip()
    for fmt in ('%Y-%m-%d', '%m/%d/%Y', '%m-%d-%Y'):
        try:
            from datetime import datetime as dt
            return dt.strptime(raw, fmt).date()
        except ValueError:
            continue
    try:
        return date.fromisoformat(raw)
    except ValueError:
        return None


@admin_required
def maintenance_list_page(request):
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()
    type_filter = request.GET.get('type', '').strip()
    records = scoped_maintenances(request.user).select_related('bus').order_by('-inspection_date')
    if query:
        records = records.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
            | Q(bus__bus_number__icontains=query) | Q(bus__route__icontains=query)
        )
    if status_filter in dict(MaintenanceRecord.STATUS_CHOICES):
        records = records.filter(status=status_filter)
    if type_filter in dict(MaintenanceRecord.TYPE_CHOICES):
        records = records.filter(record_type=type_filter)
    # Auto-flag overdue: scheduled with next_due_date in the past
    today = timezone.localdate()
    overdue_count = scoped_maintenances(request.user).filter(
        status=MaintenanceRecord.STATUS_SCHEDULED, next_due_date__lt=today
    ).count()
    paginator = Paginator(records, 10)
    page = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'maintenance/list.html', {
        'records': page, 'query': query,
        'status_filter': status_filter, 'type_filter': type_filter,
        'status_choices': MaintenanceRecord.STATUS_CHOICES,
        'type_choices': MaintenanceRecord.TYPE_CHOICES,
        'available_buses': scoped_buses(request.user).order_by('bus_number'),
        'overdue_count': overdue_count, 'today': today,
    })


@admin_required
def maintenance_get_ajax(request, pk):
    r = scoped_maintenance(request.user, pk)
    return JsonResponse({
        'id': r.id, 'bus_id': r.bus_id, 'record_type': r.record_type,
        'title': r.title, 'description': r.description,
        'inspection_date': r.inspection_date.isoformat() if r.inspection_date else '',
        'next_due_date': r.next_due_date.isoformat() if r.next_due_date else '',
        'status': r.status, 'cost': str(r.cost) if r.cost is not None else '',
    })


@admin_required
@require_POST
def maintenance_save_ajax(request):
    rid = request.POST.get('id')
    record = scoped_maintenance(request.user, rid) if rid else MaintenanceRecord()
    is_update = bool(rid)

    bus_id = request.POST.get('bus', '').strip()
    record_type = request.POST.get('record_type', MaintenanceRecord.TYPE_INSPECTION).strip()
    title = request.POST.get('title', '').strip()
    description = request.POST.get('description', '').strip()
    inspection_date = _parse_date(request.POST.get('inspection_date', ''))
    next_due_date = _parse_date(request.POST.get('next_due_date', ''))
    status = request.POST.get('status', MaintenanceRecord.STATUS_SCHEDULED).strip()
    cost_raw = request.POST.get('cost', '').strip()

    bus = scoped_buses(request.user).filter(pk=bus_id).first()
    if bus is None:
        return JsonResponse({'error': 'Select a valid bus.'}, status=400)
    if record_type not in dict(MaintenanceRecord.TYPE_CHOICES):
        return JsonResponse({'error': 'Invalid record type.'}, status=400)
    if not title:
        return JsonResponse({'error': 'Title is required.'}, status=400)
    if inspection_date is None:
        return JsonResponse({'error': 'Inspection date is required (YYYY-MM-DD).'}, status=400)
    if status not in dict(MaintenanceRecord.STATUS_CHOICES):
        return JsonResponse({'error': 'Invalid status.'}, status=400)
    cost = None
    if cost_raw:
        try:
            cost = float(cost_raw)
        except ValueError:
            return JsonResponse({'error': 'Cost must be a number.'}, status=400)
        if cost < 0:
            return JsonResponse({'error': 'Cost cannot be negative.'}, status=400)

    record.bus = bus
    record.record_type = record_type
    record.title = title
    record.description = description
    record.inspection_date = inspection_date
    record.next_due_date = next_due_date
    record.status = status
    record.cost = cost
    if not record.pk:
        record.user = request.user
    try:
        record.save()
    except IntegrityError:
        return JsonResponse({'error': 'Could not save record due to a conflict.'}, status=400)
    messages.success(request, f'Maintenance "{record.title}" {"updated" if is_update else "saved"}.')
    return JsonResponse({'status': 'success', 'id': record.id})


@admin_required
@require_POST
def maintenance_delete_ajax(request, pk):
    record = scoped_maintenance(request.user, pk)
    title = record.title
    record.delete()
    messages.success(request, f'Maintenance "{title}" deleted.')
    return JsonResponse({'status': 'deleted'})
