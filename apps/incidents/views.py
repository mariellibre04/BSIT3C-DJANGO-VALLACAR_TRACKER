from django.contrib import messages
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.scoping import scoped_buses, scoped_incident, scoped_incidents
from .models import Incident
from apps.core.permissions import admin_required


@admin_required
def incident_list_page(request):
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()
    type_filter = request.GET.get('type', '').strip()
    severity_filter = request.GET.get('severity', '').strip()
    incidents = scoped_incidents(request.user).select_related('bus').order_by('-created_at')
    if query:
        incidents = incidents.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
            | Q(location__icontains=query) | Q(bus__bus_number__icontains=query)
        )
    if status_filter in dict(Incident.STATUS_CHOICES):
        incidents = incidents.filter(status=status_filter)
    if type_filter in dict(Incident.TYPE_CHOICES):
        incidents = incidents.filter(incident_type=type_filter)
    if severity_filter in dict(Incident.SEVERITY_CHOICES):
        incidents = incidents.filter(severity=severity_filter)
    open_count = scoped_incidents(request.user).filter(
        status__in=[Incident.STATUS_REPORTED, Incident.STATUS_RESPONDING]
    ).count()
    paginator = Paginator(incidents, 10)
    page = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'incidents/list.html', {
        'incidents': page, 'query': query,
        'status_filter': status_filter, 'type_filter': type_filter,
        'severity_filter': severity_filter,
        'status_choices': Incident.STATUS_CHOICES,
        'type_choices': Incident.TYPE_CHOICES,
        'severity_choices': Incident.SEVERITY_CHOICES,
        'available_buses': scoped_buses(request.user).order_by('bus_number'),
        'open_count': open_count,
    })


@admin_required
def incident_get_ajax(request, pk):
    i = scoped_incident(request.user, pk)
    return JsonResponse({
        'id': i.id, 'bus_id': i.bus_id, 'incident_type': i.incident_type,
        'severity': i.severity, 'title': i.title, 'location': i.location,
        'description': i.description, 'status': i.status,
    })


@admin_required
@require_POST
def incident_save_ajax(request):
    iid = request.POST.get('id')
    incident = scoped_incident(request.user, iid) if iid else Incident()
    is_update = bool(iid)

    bus_id = request.POST.get('bus', '').strip()
    incident_type = request.POST.get('incident_type', Incident.TYPE_OTHER).strip()
    severity = request.POST.get('severity', Incident.SEVERITY_MEDIUM).strip()
    title = request.POST.get('title', '').strip()
    location = request.POST.get('location', '').strip()
    description = request.POST.get('description', '').strip()
    status = request.POST.get('status', Incident.STATUS_REPORTED).strip()

    bus = None
    if bus_id:
        bus = scoped_buses(request.user).filter(pk=bus_id).first()
        if bus is None:
            return JsonResponse({'error': 'Selected bus is invalid.'}, status=400)
    if incident_type not in dict(Incident.TYPE_CHOICES):
        return JsonResponse({'error': 'Invalid incident type.'}, status=400)
    if severity not in dict(Incident.SEVERITY_CHOICES):
        return JsonResponse({'error': 'Invalid severity.'}, status=400)
    if not title:
        return JsonResponse({'error': 'Title is required.'}, status=400)
    if status not in dict(Incident.STATUS_CHOICES):
        return JsonResponse({'error': 'Invalid status.'}, status=400)

    incident.bus = bus
    incident.incident_type = incident_type
    incident.severity = severity
    incident.title = title
    incident.location = location
    incident.description = description
    prev_status = incident.status if incident.pk else None
    incident.status = status
    if status in (Incident.STATUS_RESOLVED, Incident.STATUS_CLOSED) and prev_status != status:
        incident.resolved_at = timezone.now()
    if not incident.pk:
        incident.user = request.user
    try:
        incident.save()
    except IntegrityError:
        return JsonResponse({'error': 'Could not save incident due to a conflict.'}, status=400)
    messages.success(request, f'Incident "{incident.title}" {"updated" if is_update else "reported"}.')
    return JsonResponse({'status': 'success', 'id': incident.id})


@admin_required
@require_POST
def incident_resolve_ajax(request, pk):
    incident = scoped_incident(request.user, pk)
    incident.status = Incident.STATUS_RESOLVED
    incident.resolved_at = timezone.now()
    incident.save(update_fields=['status', 'resolved_at', 'updated_at'])
    messages.success(request, f'Incident "{incident.title}" marked as resolved.')
    return JsonResponse({'status': 'resolved'})


@admin_required
@require_POST
def incident_delete_ajax(request, pk):
    incident = scoped_incident(request.user, pk)
    title = incident.title
    incident.delete()
    messages.success(request, f'Incident "{title}" deleted.')
    return JsonResponse({'status': 'deleted'})
