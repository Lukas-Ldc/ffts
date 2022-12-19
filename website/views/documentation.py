from django.shortcuts import render, redirect
from website.views.functions.authentication import authorized


def documentation_view(request):

    if not authorized(request):
        return redirect('website-login')

    context = {
        'page': 'documentation',
    }
    return render(request, "documentation.html", context)
