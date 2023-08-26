"""
This is the authentication module.
"""
from django.http import HttpRequest
from django.contrib.auth.models import User
from django.utils.timezone import activate


def authorized(request: HttpRequest):
    """Verify if a user is authenticated

    Args:
        request (HttpRequest): The request

    Returns:
        bool: True if authenticated
    """
    if request.user.is_authenticated:
        activate(User.objects.get(username=request.user.username).last_name)
        return True
    else:
        return False
