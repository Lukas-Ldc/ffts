from django.shortcuts import render, redirect
from website.models import Account, Standard
from website.views.functions.authentication import authorized
from website.views.functions.importation.csv import csv_importer
from website.views.functions.importation.binance import binance_importer
from website.views.functions.importation.degiro import degiro_importer
from website.views.functions.importation.gateio import gateio_importer
from website.views.functions.importation.interactivebrokers import ib_importer


def importation_view(request, account):

    if not authorized(request):
        return redirect('website-login')

    if Account.objects.all().filter(user__exact=request.user, unique__exact=account).exists():

        if request.POST:

            if "import_csv" in request.POST:
                csv_importer(
                    request.FILES['file'],
                    request.POST['type'],
                    request.POST['oldacc'],
                    account,
                    request
                )

            elif "import_binance" in request.POST:
                binance_importer(
                    request.FILES['file'],
                    request.POST['type'],
                    request.POST['tr_type'],
                    request.POST['ac_type'],
                    account,
                    request
                )

            elif "import_degiro" in request.POST:
                degiro_importer(
                    request.FILES['file'],
                    request.POST['type'],
                    request.POST['tr_type'],
                    request.POST['ac_type'],
                    account,
                    request
                )

            elif "import_gateio" in request.POST:
                gateio_importer(
                    request.FILES['file'],
                    request.POST['type'],
                    request.POST['tr_type'],
                    request.POST['ac_type'],
                    account,
                    request
                )

            elif "import_ib" in request.POST:
                ib_importer(
                    request.FILES['file'],
                    request.POST['tr_type'],
                    request.POST['ac_type_ba'],
                    request.POST['ac_type_ia'],
                    account,
                    request
                )

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
