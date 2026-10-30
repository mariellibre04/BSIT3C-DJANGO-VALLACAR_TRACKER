from django.shortcuts import render
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Q

from apps.scoping import scoped_driver, scoped_drivers, scoped_buses
from .models import Driver
from apps.core.permissions import admin_required


@admin_required
def driver_list_page(request):
    query = request.GET.get('q', '').strip()
    drivers_list = scoped_drivers(request.user).select_related('bus').order_by('name')
    if query:
        drivers_list = drivers_list.filter(
            Q(name__icontains=query) |
            Q(license_number__icontains=query) |
            Q(contact__icontains=query) |
            Q(address__icontains=query)
        )
    paginator = Paginator(drivers_list, 10)
    drivers = paginator.get_page(request.GET.get('page', 1))
    buses = scoped_buses(request.user).order_by('bus_number')
    return render(request, 'driver/list.html', {
        'drivers': drivers, 'query': query, 'buses': buses,
    })


@admin_required
def driver_list_ajax(request):
    query = request.GET.get('q', '').strip()
    drivers_list = scoped_drivers(request.user).order_by('name')
    if query:
        drivers_list = drivers_list.filter(
            Q(name__icontains=query) |
            Q(license_number__icontains=query) |
            Q(contact__icontains=query) |
            Q(address__icontains=query)
        )
    paginator = Paginator(drivers_list, 10)
    drivers = paginator.get_page(request.GET.get('page', 1))
    data = []
    for d in drivers.object_list.select_related('bus'):
        data.append({
            'id': d.id,
            'name': d.name,
            'license_number': d.license_number,
            'contact': d.contact,
            'address': d.address,
            'bus_id': d.bus_id,
            'bus_number': d.bus.bus_number if d.bus else '',
        })
    return JsonResponse({
        'data': data,
        'has_next': drivers.has_next(),
        'has_prev': drivers.has_previous(),
        'page': drivers.number,
        'pages': drivers.paginator.num_pages,
        'total': drivers.paginator.count,
    })


@admin_required
def driver_get_ajax(request, pk):
    driver = scoped_driver(request.user, pk)
    return JsonResponse({
        'id': driver.id,
        'name': driver.name,
        'license_number': driver.license_number,
        'contact': driver.contact,
        'address': driver.address,
        'bus_id': driver.bus_id,
    })


@admin_required
@require_POST
def driver_save_ajax(request):
    driver_id = request.POST.get('id')
    if driver_id:
        driver = scoped_driver(request.user, driver_id)
        is_update = True
    else:
        driver = Driver()
        is_update = False

    name = request.POST.get('name', '').strip()
    license_number = request.POST.get('license_number', '').strip()
    contact = request.POST.get('contact', '').strip()
    address = request.POST.get('address', '').strip()
    bus_id = request.POST.get('bus', '').strip()

    if not name:
        return JsonResponse({'error': 'Name is required.'}, status=400)
    if not license_number:
        return JsonResponse({'error': 'License number is required.'}, status=400)
    if not address:
        return JsonResponse({'error': 'Address is required.'}, status=400)

    dup = Driver.objects.filter(license_number=license_number)
    if driver_id:
        dup = dup.exclude(pk=driver_id)
    if dup.exists():
        return JsonResponse({'error': 'That license number already exists.'}, status=400)

    bus = None
    if bus_id:
        buses = scoped_buses(request.user).filter(pk=bus_id)
        bus = buses.first()
        if bus is None:
            return JsonResponse({'error': 'Selected bus is invalid.'}, status=400)

    driver.name = name
    driver.license_number = license_number
    driver.contact = contact
    driver.address = address
    driver.bus = bus
    if not driver.pk:
        driver.user = request.user

    try:
        driver.save()
    except IntegrityError:
        return JsonResponse({'error': 'Could not save driver due to a conflict.'}, status=400)

    messages.success(
        request,
        f'Driver "{driver.name}" has been {"updated" if is_update else "saved"} successfully.'
    )
    return JsonResponse({
        'status': 'success',
        'id': driver.id,
        'name': driver.name,
        'license_number': driver.license_number,
        'contact': driver.contact,
        'address': driver.address,
        'bus_id': driver.bus_id,
    })


@admin_required
@require_POST
def driver_delete_ajax(request, pk):
    driver = scoped_driver(request.user, pk)
    name = driver.name
    driver.delete()
    messages.success(request, f'Driver "{name}" has been deleted successfully.')
    return JsonResponse({'status': 'deleted'})
