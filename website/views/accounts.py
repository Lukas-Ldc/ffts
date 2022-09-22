import website.views.functions.authentication as auth
from django.shortcuts import render, redirect
from website.models import Account, Standard
from django.contrib.auth import authenticate

def accounts_view(request):

    if not auth.amIauthorized(request):
        return redirect('website-login')

    if request.method == 'POST':

        if "add_account" in request.POST:
            Account.objects.create(unique='.', name=request.POST['name'], type=request.POST['type'], user=request.user, group=request.POST['group'], unit=request.POST['unit'], gmt=request.POST['gmt'], comment=request.POST['comment'])

        if "modify_account" in request.POST:
            if Account.objects.all().filter(user__exact=request.user, name__exact=request.POST['name']).exists():
                updated_acc = Account.objects.all().get(user__exact=request.user, name__exact=request.POST['name'])
                if len(request.POST['type']) > 0: updated_acc.type = request.POST['type']
                if len(request.POST['group']) > 0: updated_acc.group = request.POST['group']
                if len(request.POST['unit']) > 0: updated_acc.unit = request.POST['unit']
                if len(request.POST['gmt']) > 0: updated_acc.gmt = request.POST['gmt']
                if len(request.POST['comment']) > 0: updated_acc.comment = request.POST['comment']
                updated_acc.save()

        if "delete_account" in request.POST:
            if authenticate(request, username=request.user.username, password=request.POST['pass']):
                Account.objects.all().filter(user__exact=request.user, name__exact=request.POST['name']).delete()

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
