import imp
import website.views.functions.authentication as auth
from django.shortcuts import render, redirect
from website.models import Account
from website.views.functions.importation.csv import csv_importer


def importation_view(request, account):

    if not auth.amIauthorized(request):
        return redirect('website-login')

    if Account.objects.all().filter(user__exact=request.user, unique__exact=account).exists():

        if request.POST:

            if "import_csv" in request.POST:
                csv_importer(request.FILES['file'], request.POST['type'], request.POST['feeunit'], request.POST['feecalcul'], Account.objects.all().get(user__exact=request.user, unique__exact=account).unit)

        the_account = Account.objects.all().get(user__exact=request.user, unique__exact=account)

        context = {
            'page': 'importation',
            'account': the_account,
        }
        return render(request, "importation.html", context)
    
    else:
        return redirect('website-accounts')
