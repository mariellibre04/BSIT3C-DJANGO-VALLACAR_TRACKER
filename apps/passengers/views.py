from django.shortcuts import render
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError
from django.db.models import Q

from apps.scoping import scoped_passenger, scoped_passengers, scoped_buses
from apps.bus.models import Bus
from .models import Passenger
from apps.core.permissions import admin_required

MIN_AGE = 1
MAX_AGE = 150


def _parse_age(raw_age):
    try:
        return int(raw_age)
    except (TypeError, ValueError):
        return None


@admin_required
def passenger_list_page(request):
    query = request.GET.get('q', '').strip()
    type_filter = request.GET.get('type', '').strip()
    passengers_list = scoped_passengers(request.user).select_related('bus').order_by('name')
    if query:
        passengers_list = passengers_list.filter(
            Q(name__icontains=query) |
            Q(contact__icontains=query) |
            Q(address__icontains=query) |
            Q(email__icontains=query)
        )
    if type_filter in dict(Passenger.TYPE_CHOICES):
        passengers_list = passengers_list.filter(passenger_type=type_filter)
    paginator = Paginator(passengers_list, 10)
    passengers = paginator.get_page(request.GET.get('page', 1))
    available_buses = scoped_buses(request.user).filter(
        status=Bus.STATUS_ACTIVE
    ).order_by('bus_number')
    return render(request, 'passengers/list.html', {
        'passengers': passengers, 'query': query,
        'type_filter': type_filter,
        'type_choices': Passenger.TYPE_CHOICES,
        'available_buses': available_buses,
    })


@admin_required
def passenger_list_ajax(request):
    query = request.GET.get('q', '').strip()
    passengers_list = scoped_passengers(request.user).order_by('name')
    if query:
        passengers_list = passengers_list.filter(
            Q(name__icontains=query) |
            Q(contact__icontains=query) |
            Q(address__icontains=query) |
            Q(email__icontains=query)
        )
    paginator = Paginator(passengers_list, 10)
    passengers = paginator.get_page(request.GET.get('page', 1))
    data = []
    for p in passengers.object_list.select_related('bus'):
        data.append({
            'id': p.id,
            'name': p.name,
            'age': p.age,
            'passenger_type': p.passenger_type,
            'passenger_type_display': p.get_passenger_type_display(),
            'contact': p.contact,
            'address': p.address,
            'email': p.email,
            'bus_id': p.bus_id,
            'bus_number': p.bus.bus_number if p.bus else '',
            'bus_route': p.bus.route if p.bus else '',
        })
    return JsonResponse({
        'data': data,
        'has_next': passengers.has_next(),
        'has_prev': passengers.has_previous(),
        'page': passengers.number,
        'pages': passengers.paginator.num_pages,
        'total': passengers.paginator.count,
    })


@admin_required
def passenger_get_ajax(request, pk):
    passenger = scoped_passenger(request.user, pk)
    return JsonResponse({
        'id': passenger.id,
        'name': passenger.name,
        'age': passenger.age,
        'passenger_type': passenger.passenger_type,
        'contact': passenger.contact,
        'address': passenger.address,
        'email': passenger.email,
        'bus_id': passenger.bus_id,
    })


@admin_required
@require_POST
def passenger_save_ajax(request):
    passenger_id = request.POST.get('id')
    if passenger_id:
        passenger = scoped_passenger(request.user, passenger_id)
        is_update = True
    else:
        passenger = Passenger()
        is_update = False

    name = request.POST.get('name', '').strip()
    age = request.POST.get('age', '').strip()
    passenger_type = request.POST.get('passenger_type', Passenger.TYPE_REGULAR).strip()
    contact = request.POST.get('contact', '').strip()
    address = request.POST.get('address', '').strip()
    email = request.POST.get('email', '').strip()
    bus_id = request.POST.get('bus', '').strip()

    if not name:
        return JsonResponse({'error': 'Name is required.'}, status=400)
    if not age:
        return JsonResponse({'error': 'Age is required.'}, status=400)
    age_value = _parse_age(age)
    if age_value is None or age_value < MIN_AGE or age_value > MAX_AGE:
        return JsonResponse(
            {'error': f'Age must be a number between {MIN_AGE} and {MAX_AGE}.'},
            status=400,
        )
    if passenger_type not in dict(Passenger.TYPE_CHOICES):
        return JsonResponse({'error': 'Invalid passenger type. Choose Student, Senior Citizen, Regular, or PWD.'}, status=400)
    if not address:
        return JsonResponse({'error': 'Address is required.'}, status=400)
    if email:
        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({'error': 'Enter a valid email address.'}, status=400)

    bus = None
    if bus_id:
        bus = scoped_buses(request.user).filter(pk=bus_id).first()
        if bus is None:
            return JsonResponse({'error': 'Selected bus is invalid.'}, status=400)
        occupied = bus.passengers.count()
        staying = passenger.pk is not None and passenger.bus_id == bus.pk
        if not staying and occupied >= bus.capacity:
            return JsonResponse(
                {'error': f'Bus "{bus.bus_number}" is full ({bus.capacity} seats).'},
                status=400,
            )

    passenger.name = name
    passenger.age = age_value
    passenger.passenger_type = passenger_type
    passenger.contact = contact
    passenger.address = address
    passenger.email = email
    passenger.bus = bus
    if not passenger.pk:
        passenger.user = request.user

    try:
        passenger.save()
    except IntegrityError:
        return JsonResponse({'error': 'Could not save passenger due to a conflict.'}, status=400)

    messages.success(
        request,
        f'Passenger "{passenger.name}" has been {"updated" if is_update else "saved"} successfully.'
    )
    return JsonResponse({
        'status': 'success',
        'id': passenger.id,
        'name': passenger.name,
        'age': passenger.age,
        'passenger_type': passenger.passenger_type,
        'contact': passenger.contact,
        'address': passenger.address,
        'email': passenger.email,
        'bus_id': passenger.bus_id,
    })


@admin_required
@require_POST
def passenger_delete_ajax(request, pk):
    passenger = scoped_passenger(request.user, pk)
    name = passenger.name
    passenger.delete()
    messages.success(request, f'Passenger "{name}" has been deleted successfully.')
    return JsonResponse({'status': 'deleted'})
