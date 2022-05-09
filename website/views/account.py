import website.views.functions.authentication as auth
from django.shortcuts import render, redirect


def account_view(request, name):

    if not auth.amIauthorized(request):
        return redirect('website-login')

    context = {
        'page': 'account',
    }
    return render(request, "account.html", context)