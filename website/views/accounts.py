from zoneinfo import available_timezones, ZoneInfo, ZoneInfoNotFoundError
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from website.models import Account, Standard
from website.views.functions.authentication import authorized
from website.views.functions.dbinterface import add_account, mod_account, del_account


def accounts_view(request):
    """The view for the accounts page

    Args:
        request (HttpRequest): The request for the accounts page

    Returns:
        HttpResponse: The accounts page
    """

    if not authorized(request):
        return redirect('website-login')

    if request.method == "POST":

        if "change_timezone" in request.POST.keys():
            uzer = User.objects.get(username=request.user.username)
            try:
                uzer.last_name = ZoneInfo(request.POST['change_timezone'])  # Last Name for UTC storage (ugly but easy)
                uzer.save()
            except (ValueError, ZoneInfoNotFoundError):
                pass

        # The user wants to create an account
        if "add_account" in request.POST.keys():
            add_account(
                request,
                True,
                request.POST['name'],
                request.POST['type'],
                request.POST['group'],
                request.POST['unit'],
                request.POST['utc'],
                request.POST['open_date'],
                request.POST['close_date'],
                request.POST['comment']
            )

        # The user wants to modify an account
        if "modify_account" in request.POST.keys():
            mod_account(
                request,
                True,
                request.POST['name'],
                request.POST['type'],
                request.POST['group'],
                request.POST['unit'],
                request.POST['utc'],
                request.POST['open_date'],
                request.POST['close_date'],
                request.POST['comment']
            )

        # The user wants to delete an account
        if "delete_account" in request.POST.keys():
            if authenticate(request, username=request.user.username, password=request.POST['pass']):
                del_account(request, request.POST['name'])

    # Web page context data
    user_accounts = Account.objects.all().filter(user__exact=request.user.username).order_by('group', 'name')
    user_acc_groups = user_accounts.values('group').order_by('group').distinct()
    acc_types = Standard.objects.all().filter(type__exact='AccountType').order_by('name')

    # Web page rendering
    context = {
        'file': 'accounts',
        'title': f"Accounts - {request.user.username}",
        'accounts': user_accounts,
        'groups': user_acc_groups,
        'user': request.user.username,
        'staff': request.user.is_staff,
        'types': acc_types,
        'timezones': sorted(available_timezones()),
        'user_tz': User.objects.get(username=request.user.username).last_name,
        'today': datetime.now().strftime("%Y-%m-%d")
    }
    return render(request, "accounts.html", context)
