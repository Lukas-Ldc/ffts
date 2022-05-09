import website.views.functions.authentication as auth
from django.shortcuts import render, redirect


def accounts_view(request):

    if not auth.amIauthorized(request):
        return redirect('website-login')

    context = {
        'page': 'accounts',
    }
    return render(request, "accounts.html", context)