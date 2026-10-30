from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Q

from apps.core.permissions import admin_required
from apps.core.roles import ROLE_ADMIN, ROLE_LABELS, get_role, set_role


# PAGE
@admin_required
def user_list_page(request):
    query = request.GET.get('q', '').strip()

    users_list = User.objects.all().order_by('-date_joined')

    if query:
        users_list = users_list.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )

    paginator = Paginator(users_list, 10)
    page_number = request.GET.get('page', 1)
    users = paginator.get_page(page_number)
    for account in users:
        account.role = get_role(account)
        account.role_label = ROLE_LABELS[account.role]

    return render(request, 'users/list.html', {
        'users': users,
        'query': query,
    })


# LIST USERS (AJAX)
@admin_required
def user_list_ajax(request):
    users_list = User.objects.all().order_by('-date_joined')
    paginator = Paginator(users_list, 10)
    page_number = request.GET.get('page', 1)
    users = paginator.get_page(page_number)
    data = []
    for account in users.object_list:
        role = get_role(account)
        data.append({
            'id': account.id,
            'username': account.username,
            'first_name': account.first_name,
            'last_name': account.last_name,
            'email': account.email,
            'is_staff': account.is_staff,
            'is_active': account.is_active,
            'date_joined': account.date_joined,
            'role': role,
            'role_label': ROLE_LABELS[role],
        })
    return JsonResponse({
        "data":     data,
        "has_next": users.has_next(),
        "has_prev": users.has_previous(),
        "page":     users.number,
        "pages":    users.paginator.num_pages,
        "total":    users.paginator.count,
    })


# GET SINGLE USER (AJAX)
@admin_required
def user_get_ajax(request, pk):
    user = get_object_or_404(User, pk=pk)
    role = get_role(user)
    return JsonResponse({
        "id":         user.id,
        "username":   user.username,
        "first_name": user.first_name,
        "last_name":  user.last_name,
        "email":      user.email,
        "is_staff":   user.is_staff,
        "is_active":  user.is_active,
        "role":       role,
        "role_label": ROLE_LABELS[role],
    })


# CREATE / UPDATE USER (AJAX)
@admin_required
@require_POST
def user_save_ajax(request):
    user_id = request.POST.get("id")

    if user_id:
        user = get_object_or_404(User, pk=user_id)
        is_update = True
    else:
        user = User()
        is_update = False

    username = request.POST.get("username", "").strip()
    email = request.POST.get("email", "").strip()

    if not username:
        return JsonResponse({"error": "Username is required."}, status=400)

    dup_qs = User.objects.filter(Q(username=username) | (Q(email=email) & ~Q(email="")))
    if user_id:
        dup_qs = dup_qs.exclude(pk=user_id)
    if dup_qs.filter(username=username).exists():
        return JsonResponse({"error": "That username is already taken."}, status=400)
    if email and dup_qs.filter(email=email).exists():
        return JsonResponse({"error": "That email is already in use."}, status=400)

    user.username   = username
    user.first_name = request.POST.get("first_name", "")
    user.last_name  = request.POST.get("last_name", "")
    user.email      = email
    user.is_active  = request.POST.get("is_active") == "true"

    password = request.POST.get("password")
    if password:
        user.set_password(password)
    elif not user_id:
        return JsonResponse({"error": "Password is required for new users."}, status=400)

    try:
        user.save()
    except IntegrityError:
        return JsonResponse({"error": "Could not save user due to a conflict (duplicate username/email)."}, status=400)

    role = request.POST.get("role", "").strip()
    if role not in ROLE_LABELS:
        role = ROLE_ADMIN if request.POST.get("is_staff") == "true" else "passenger"
    role = set_role(user, role)

    messages.success(
        request,
        f'User "{user.username}" has been {"updated" if is_update else "saved"} successfully.'
    )

    return JsonResponse({
        "status": "success",
        "id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "is_staff": user.is_staff,
        "is_active": user.is_active,
        "role": role,
        "role_label": ROLE_LABELS[role],
    })


# DELETE USER (AJAX)
@admin_required
@require_POST
def user_delete_ajax(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.user == user:
        return JsonResponse({"error": "You cannot delete yourself"}, status=400)
    username = user.username
    user.delete()
    return JsonResponse({
        "status": "deleted",
        "message": f'User "{username}" has been deleted successfully.',
    })