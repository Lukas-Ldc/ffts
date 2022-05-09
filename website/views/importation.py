import website.views.functions.authentication as auth
from django.shortcuts import render, redirect


def importation_view(request):

    if not auth.amIauthorized(request):
        return redirect('website-login')

    context = {
        'page': 'importation',
    }
    return render(request, "importation.html", context)