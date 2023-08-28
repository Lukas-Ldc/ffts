from csv import writer as csvwriter
from decimal import Decimal
from datetime import datetime
from zoneinfo import ZoneInfo, available_timezones
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.db.models import Q
from django.http import HttpResponse, HttpRequest
from django.contrib.auth.models import User
from website.models import Transfer, Account
from website.views.functions.authentication import authorized
from website.views.functions.dbinterface import add_transfer, mod_transfer, del_transfer


def transfers_view(request: HttpRequest, account: str):
    """The view for the transfers page

    Args:
        request (HttpRequest): The request for the transfers page
        account (str): The name of the account

    Returns:
        HttpResponse: The transfers page or the export of the transfers
    """

    if not authorized(request):
        return redirect('website-login')

    # If the account belongs to the user who made the request
    if Account.objects.all().filter(user__exact=request.user, unique__exact=account).exists():

        if request.method == "POST":

            # The user wants to export the transfers
            if "export" in request.POST.keys():
                return transfers_export(account, request)

            # The user wants to add a transfer
            if "add_transfer" in request.POST.keys():
                add_transfer(
                    request,
                    False,
                    True,
                    request.POST['timezone'],
                    request.POST['source'],
                    request.POST['destination'],
                    request.POST['date'],
                    request.POST['unit'],
                    request.POST['amount'],
                    request.POST['fee'],
                    request.POST['feeunit'],
                    request.POST['comment']
                )

            # The user wants to modify transfers
            if "modify_transfer" in request.POST.keys():
                for tr_id in str(request.POST['id']).split(','):
                    mod_transfer(
                        request,
                        True,
                        request.POST['timezone'],
                        tr_id,
                        request.POST['source'],
                        request.POST['destination'],
                        request.POST['date'],
                        request.POST['unit'],
                        request.POST['amount'],
                        request.POST['fee'],
                        request.POST['feeunit'],
                        request.POST['comment']
                    )

            # The user wants to delete transfers
            if "delete_transfer" in request.POST.keys():
                if authenticate(request, username=request.user.username, password=request.POST['pass']):
                    for tr_id in str(request.POST['id']).split(','):
                        del_transfer(request, tr_id)

        # Web page context data
        the_account = Account.objects.all().get(user__exact=request.user, unique__exact=account)
        transfers = Transfer.objects.all().filter(Q(source__exact=account) | Q(destination__exact=account)).order_by('-date')
        accounts = Account.objects.all().filter(user__exact=request.user).order_by('name')

        # Web page rendering
        context = {
            'file': 'transfers',
            'title': f"Transfers - {the_account.name}",
            'transfers': transfers,
            'account': the_account,
            'accounts': accounts,
            'timezones': sorted(available_timezones()),
        }
        return render(request, "transfers.html", context)

    # Account + User did not matched
    return redirect('website-accounts')


def transfers_export(account: Account, request: HttpRequest):
    """Exports in a CSV all the transfers of an account.

    Args:
        account (Account): The account linked to the transfers
        request (HttpRequest): The request made to get the export

    Returns:
        HttpResponse: The CSV file
    """
    # Date used in the file name
    date = datetime.now().strftime("%Y/%m/%d-%H-%M")
    # Creating the file and putting it in an HTTP response
    response = HttpResponse(content_type='text/csv',
                            headers={'Content-Disposition': 'attachment; \
                                    filename=ffts_"' + str(account).replace(" ", "_") + '_transfers_' + date + '.csv"'})

    # Writting each transaction in the file
    writer = csvwriter(response)
    header = [str(field).split(".")[-1].replace("_", " ").title() for field in Transfer._meta.fields]
    header.remove("Id")
    writer.writerow(header)

    for trans in Transfer.objects.all().filter(Q(source__exact=account) | Q(destination__exact=account)).order_by('-date'):
        writer.writerow([
            acc_clean(trans.source),
            acc_clean(trans.destination),
            str(trans.date.astimezone(ZoneInfo(User.objects.get(username=request.user.username).last_name))),
            trans.unit,
            exp_num(trans.amount),
            exp_num(trans.fee),
            trans.fee_unit,
            trans.comment
        ])

    # Returning the file to download
    return response


def acc_clean(account: str):
    """Cleans an account object name:
    "Account object (acc_name)" -> "acc_name"

    Args:
        account (str): The account object name

    Returns:
        str: The account name
    """
    return str(account).replace("Account object (", "")[:-1]


def exp_num(number: float):
    """Clean any number given:
    '140.93000000' -> '140.93',
    '140.0000' -> '140'

    Args:
        number (float): The number to clean

    Returns:
        float or int: The cleaned number
    """
    if number is not None:
        return number.quantize(Decimal(1)) if number == number.to_integral() else number.normalize()
    return ""
