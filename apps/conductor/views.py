from django.shortcuts import render
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Q

from apps.scoping import scoped_conductor, scoped_conductors, scoped_buses
from .models import Conductor
from apps.core.permissions import admin_required


@admin_required
def conductor_list_page(request):
    query = request.GET.get('q', '').strip()
    conductors_list = scoped_conductors(request.user).select_related('bus').order_by('name')
    if query:
        conductors_list = conductors_list.filter(
            Q(name__icontains=query) |
            Q(employee_id__icontains=query) |
            Q(contact__icontains=query) |
            Q(address__icontains=query)
        )
    paginator = Paginator(conductors_list, 10)
    conductors = paginator.get_page(request.GET.get('page', 1))
    buses = scoped_buses(request.user).order_by('bus_number')
    return render(request, 'conductor/list.html', {
        'conductors': conductors, 'query': query, 'buses': buses,
    })


@admin_required
def conductor_list_ajax(request):
    query = request.GET.get('q', '').strip()
    conductors_list = scoped_conductors(request.user).order_by('name')
    if query:
        conductors_list = conductors_list.filter(
            Q(name__icontains=query) |
            Q(employee_id__icontains=query) |
            Q(contact__icontains=query) |
            Q(address__icontains=query)
        )
    paginator = Paginator(conductors_list, 10)
    conductors = paginator.get_page(request.GET.get('page', 1))
    data = []
    for c in conductors.object_list.select_related('bus'):
        data.append({
            'id': c.id,
            'name': c.name,
            'employee_id': c.employee_id,
            'contact': c.contact,
            'address': c.address,
            'bus_id': c.bus_id,
            'bus_number': c.bus.bus_number if c.bus else '',
        })
    return JsonResponse({
        'data': data,
        'has_next': conductors.has_next(),
        'has_prev': conductors.has_previous(),
        'page': conductors.number,
        'pages': conductors.paginator.num_pages,
        'total': conductors.paginator.count,
    })


@admin_required
def conductor_get_ajax(request, pk):
    conductor = scoped_conductor(request.user, pk)
    return JsonResponse({
        'id': conductor.id,
        'name': conductor.name,
        'employee_id': conductor.employee_id,
        'contact': conductor.contact,
        'address': conductor.address,
        'bus_id': conductor.bus_id,
    })


@admin_required
@require_POST
def conductor_save_ajax(request):
    conductor_id = request.POST.get('id')
    if conductor_id:
        conductor = scoped_conductor(request.user, conductor_id)
        is_update = True
    else:
        conductor = Conductor()
        is_update = False

    name = request.POST.get('name', '').strip()
    employee_id = request.POST.get('employee_id', '').strip()
    contact = request.POST.get('contact', '').strip()
    address = request.POST.get('address', '').strip()
    bus_id = request.POST.get('bus', '').strip()

    if not name:
        return JsonResponse({'error': 'Name is required.'}, status=400)
    if not employee_id:
        return JsonResponse({'error': 'Employee ID is required.'}, status=400)
    if not address:
        return JsonResponse({'error': 'Address is required.'}, status=400)

    dup = Conductor.objects.filter(employee_id=employee_id)
    if conductor_id:
        dup = dup.exclude(pk=conductor_id)
    if dup.exists():
        return JsonResponse({'error': 'That employee ID already exists.'}, status=400)

    bus = None
    if bus_id:
        buses = scoped_buses(request.user).filter(pk=bus_id)
        bus = buses.first()
        if bus is None:
            return JsonResponse({'error': 'Selected bus is invalid.'}, status=400)

    conductor.name = name
    conductor.employee_id = employee_id
    conductor.contact = contact
    conductor.address = address
    conductor.bus = bus
    if not conductor.pk:
        conductor.user = request.user

    try:
        conductor.save()
    except IntegrityError:
        return JsonResponse({'error': 'Could not save conductor due to a conflict.'}, status=400)

    messages.success(
        request,
        f'Conductor "{conductor.name}" has been {"updated" if is_update else "saved"} successfully.'
    )
    return JsonResponse({
        'status': 'success',
        'id': conductor.id,
        'name': conductor.name,
        'employee_id': conductor.employee_id,
        'contact': conductor.contact,
        'address': conductor.address,
        'bus_id': conductor.bus_id,
    })


@admin_required
@require_POST
def conductor_delete_ajax(request, pk):
    conductor = scoped_conductor(request.user, pk)
    name = conductor.name
    conductor.delete()
    messages.success(request, f'Conductor "{name}" has been deleted successfully.')
    return JsonResponse({'status': 'deleted'})
