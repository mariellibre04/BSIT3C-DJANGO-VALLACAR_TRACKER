from .permissions import role_context


def role(request):
    return role_context(request)
