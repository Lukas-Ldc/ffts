"""
This is the authentication module.
"""
from django.http import HttpRequest


def authorized(request: HttpRequest):
    """Verify if a user is authenticated

    Args:
        request (HttpRequest): The request

    Returns:
        bool: True if authenticated
    """
    if request.user.is_authenticated:
        return True
    else:
        return False
