import website.views.functions.authentication as auth
from django.shortcuts import render, redirect


def documentation_view(request):

    if not auth.amIauthorized(request):
        return redirect('website-login')

    context = {
        'page': 'documentation',
    }
    return render(request, "documentation.html", context)