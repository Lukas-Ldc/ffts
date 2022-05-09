from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login


def login_view(request):

    context = {
        'page': 'login',
    }
    return render(request, "login.html", context)
