from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login


def login_view(request):

    login_message = 0
    if request.method == 'POST':
        uAuth = authenticate(request, username=request.POST['user'], password=request.POST['pass'])
        if uAuth is not None:
             login(request, uAuth)
             return redirect('website-accounts')
        else:
            login_message = 1

    context = {
        'page': 'login',
        'log': login_message,
    }
    return render(request, "login.html", context)
