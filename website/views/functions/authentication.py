def authorized(request):
    if request.user.is_authenticated:
        return True
    else:
        return False
