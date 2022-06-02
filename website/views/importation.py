import website.views.functions.authentication as auth
from django.shortcuts import render, redirect
from website.models import Account, Standard
from website.views.functions.importation.csv import csv_importer
from website.views.functions.importation.binance import binance_importer
from website.views.functions.importation.degiro import degiro_importer
from website.views.functions.importation.interactivebrokers import ib_importer


def importation_view(request, account):

    if not auth.amIauthorized(request):
        return redirect('website-login')

    if Account.objects.all().filter(user__exact=request.user, unique__exact=account).exists():

        if request.POST:

            if "import_csv" in request.POST:
                csv_importer(request.FILES['file'], request.POST['type'], request.POST['feeunit'], str(Account.objects.all().get(user__exact=request.user, unique__exact=account).unit).split(",")[0])

            if "import_binance" in request.POST:
                binance_importer(request.FILES['file'], request.POST['type'], request.POST['tr_type'], request.POST['ac_type'], Account.objects.all().get(user__exact=request.user, unique__exact=account).unique)

            if "import_degiro" in request.POST:
                degiro_importer(request.FILES['file'], request.POST['type'], request.POST['tr_type'], request.POST['ac_type'], Account.objects.all().get(user__exact=request.user, unique__exact=account).unique)

            if "import_ib" in request.POST:
                ib_importer(request.FILES['file'], request.POST['tr_type'], request.POST['ac_type'], Account.objects.all().get(user__exact=request.user, unique__exact=account).unique)

        the_account = Account.objects.all().get(user__exact=request.user, unique__exact=account)
        tr_types = Standard.objects.all().filter(type__exact='TransactionType').order_by('name')
        accounts = Account.objects.all().filter(user__exact=request.user)

        context = {
            'page': 'importation',
            'account': the_account,
            'tr_types': tr_types,
            'accounts': accounts,
        }
        return render(request, "importation.html", context)
    
    else:
        return redirect('website-accounts')
