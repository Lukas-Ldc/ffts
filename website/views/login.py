from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User


def login_view(request):
    """The view for the login page

    Args:
        request (HttpRequest): The request for the login page

    Returns:
        HttpResponse: The login page or the accounts page
    """

    login_message = 0

    if request.method == 'POST':

        # Trying to authenticate the user
        user_auth = authenticate(request, username=request.POST['user'], password=request.POST['pass'])
        if user_auth is not None:

            # Setting TimeZone if none (last_name field used)
            uzer = User.objects.get(username=request.POST['user'])
            try:
                ZoneInfo(uzer.last_name)
            except(ValueError, ZoneInfoNotFoundError):
                uzer.last_name = "UTC"
                uzer.save()

            login(request, user_auth)
            return redirect('website-accounts')
        else:
            # Login or password incorect
            login_message = 1

    # Web page rendering
    context = {
        'file': 'login',
        'title': "Login",
        'log': login_message,
    }
    return render(request, "login.html", context)
