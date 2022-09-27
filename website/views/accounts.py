import website.views.functions.authentication as auth
from django.shortcuts import render, redirect
from website.models import Account, Standard
from django.contrib.auth import authenticate
import website.views.functions.dbinterface as dbi

def accounts_view(request):

    if not auth.amIauthorized(request):
        return redirect('website-login')

    if request.method == 'POST':

        if "add_account" in request.POST:
            dbi.addAccount(request, request.POST['name'], request.POST['type'], request.POST['group'], request.POST['unit'], request.POST['gmt'], request.POST['comment'])

        if "modify_account" in request.POST:
            dbi.modAccount(request, request.POST['name'], request.POST['type'], request.POST['group'], request.POST['unit'], request.POST['gmt'], request.POST['comment'])

        if "delete_account" in request.POST:
            if authenticate(request, username=request.user.username, password=request.POST['pass']):
                dbi.delAccount(request, request.POST['name'])

    user_Accounts = Account.objects.all().filter(user__exact=request.user.username).order_by('group','name')
    user_Acc_Groups = user_Accounts.values('group').order_by('group').distinct()
    acc_Types = Standard.objects.all().filter(type__exact='AccountType').order_by('name')

    context = {
        'page': 'accounts',
        'accounts': user_Accounts,
        'groups': user_Acc_Groups,
        'user': request.user.username,
        'staff': request.user.is_staff,
        'types': acc_Types,
    }
    return render(request, "accounts.html", context)
