from django.shortcuts import render, redirect
from website.views.functions.authentication import authorized


def documentation_view(request):
    """The view for the documentation page

    Args:
        request (HttpRequest): The request for the documentation page

    Returns:
        HttpResponse: The documentation page
    """

    if not authorized(request):
        return redirect('website-login')

    # Web page rendering
    context = {
        'file': 'documentation',
        'title': f"Documentation - {request.user.username}",
    }
    return render(request, "documentation.html", context)
