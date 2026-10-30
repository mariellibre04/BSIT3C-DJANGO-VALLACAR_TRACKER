"""Role-based view decorators for the three Vallacar dashboards."""

from functools import wraps

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse

from .roles import (
    ROLE_ADMIN,
    ROLE_CONDUCTOR,
    ROLE_LABELS,
    ROLE_PASSENGER,
    get_role,
    landing_url_name,
)


def _wants_json(request):
    return (
        request.path.startswith('/api/')
        or request.headers.get('x-requested-with') == 'XMLHttpRequest'
        or 'application/json' in request.headers.get('accept', '')
    )


def role_required(*allowed_roles):
    """Allow only the given roles; send everyone else to their own dashboard."""
    allowed = set(allowed_roles) or {ROLE_ADMIN}

    def decorator(view):
        @wraps(view)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(f"{reverse('login')}?next={request.get_full_path()}")

            role = get_role(request.user)
            if role in allowed:
                return view(request, *args, **kwargs)

            if _wants_json(request):
                return JsonResponse(
                    {'error': 'You do not have access to this action.'}, status=403
                )

            messages.error(
                request,
                f'{ROLE_LABELS[role]} accounts cannot open that page.',
            )
            return redirect(landing_url_name(role))

        return _wrapped

    return decorator


admin_required = role_required(ROLE_ADMIN)
conductor_required = role_required(ROLE_ADMIN, ROLE_CONDUCTOR)
passenger_required = role_required(ROLE_PASSENGER)


def role_context(request):
    role = get_role(request.user)
    return {
        'user_role': role,
        'user_role_label': ROLE_LABELS[role],
        'is_admin_user': role == ROLE_ADMIN,
        'is_conductor_user': role == ROLE_CONDUCTOR,
        'is_passenger_user': role == ROLE_PASSENGER,
    }
