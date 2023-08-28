from django.http import HttpRequest
from django.shortcuts import redirect
from django.contrib.auth import logout


def logout_view(request: HttpRequest):
    """The view for the logout page

    Args:
        request (HttpRequest): The request for the logout

    Returns:
        HttpResponse: The login page
    """
    logout(request)
    return redirect('website-login')
