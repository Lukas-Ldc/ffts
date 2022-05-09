import website.views.functions.authentication as auth
from django.shortcuts import render, redirect


def transactions_view(request, account):

    if not auth.amIauthorized(request):
        return redirect('website-login')

    context = {
        'page': 'transactions',
    }
    return render(request, "transactions.html", context)