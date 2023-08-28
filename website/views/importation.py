from zoneinfo import available_timezones
from django.http import HttpRequest
from django.shortcuts import render, redirect
from website.models import Account, Standard
from website.views.functions.authentication import authorized
from website.views.functions.importation.csv import csv_importer
from website.views.functions.importation.binance import binance_importer
from website.views.functions.importation.degiro import degiro_importer
from website.views.functions.importation.estateguru import estateguru_importer
from website.views.functions.importation.gateio import gateio_importer
from website.views.functions.importation.interactivebrokers import ib_importer


def importation_view(request: HttpRequest, account: str):
    """The view for the importation page

    Args:
        request (HttpRequest): The request for the importation page
        account (str): The name of the account

    Returns:
        HttpResponse: The importation page
    """

    if not authorized(request):
        return redirect('website-login')

    # If the account belongs to the user who made the request
    if Account.objects.all().filter(user__exact=request.user, unique__exact=account).exists():

        if request.method == "POST":

            # The user wants to import a CSV file
            if "import_csv" in request.POST.keys():
                csv_importer(
                    request.FILES['file'],
                    request.POST['type'],
                    request.POST['transf_acc'],
                    account,
                    request,
                    request.POST['timezone'],
                )

            # The user wants to import data from binance
            elif "import_binance" in request.POST.keys():
                binance_importer(
                    request.FILES['file'],
                    request.POST['type'],
                    request.POST['tr_type'],
                    request.POST['transf_acc'],
                    account,
                    request,
                    request.POST['timezone'],
                )

            # The user wants to import data from Degiro
            elif "import_degiro" in request.POST.keys():
                degiro_importer(
                    request.FILES['file'],
                    request.POST['type'],
                    request.POST['tr_type'],
                    request.POST['bank_acc'],
                    account,
                    request,
                    request.POST['timezone'],
                )

            # The user wants to import data from EstateGuru
            elif "import_estateguru" in request.POST.keys():
                estateguru_importer(
                    request.FILES['file'],
                    request.POST['bank_acc'],
                    account,
                    request,
                    request.POST['timezone'],
                )

            # The user wants to import data from Gate.io
            elif "import_gateio" in request.POST.keys():
                gateio_importer(
                    request.FILES['file'],
                    request.POST['type'],
                    request.POST['tr_type'],
                    request.POST['transf_acc'],
                    account,
                    request,
                    request.POST['timezone'],
                )

            # The user wants to import data from InteractiveBrokers
            elif "import_ib" in request.POST.keys():
                ib_importer(
                    request.FILES['file'],
                    request.POST['tr_type'],
                    request.POST['bank_acc'],
                    request.POST['ib_acc'],
                    account,
                    request,
                    request.POST['timezone'],
                )

        # Web page context data
        the_account = Account.objects.all().get(user__exact=request.user, unique__exact=account)
        tr_types = Standard.objects.all().filter(type__exact='TransactionType').order_by('name')
        accounts = Account.objects.all().filter(user__exact=request.user)

        # Web page rendering
        context = {
            'file': 'importation',
            'title': f"Importation - {the_account.name}",
            'account': the_account,
            'tr_types': tr_types,
            'accounts': accounts,
            'timezones': sorted(available_timezones()),
        }
        return render(request, "importation.html", context)

    # Account + User did not matched
    return redirect('website-accounts')
