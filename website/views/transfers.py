import website.views.functions.authentication as auth
from django.shortcuts import render, redirect


def transfers_view(request, account):

    if not auth.amIauthorized(request):
        return redirect('website-login')

    context = {
        'page': 'transfers',
    }
    return render(request, "transfers.html", context)