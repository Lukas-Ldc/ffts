from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login


def login_view(request):

    login_message = 0
    if request.method == 'POST':
        user_auth = authenticate(request, username=request.POST['user'], password=request.POST['pass'])
        if user_auth is not None:
            login(request, user_auth)
            return redirect('website-accounts')
        else:
            login_message = 1

    context = {
        'page': 'login',
        'log': login_message,
    }
    return render(request, "login.html", context)
