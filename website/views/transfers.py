from csv import writer as csvwriter
from decimal import Decimal
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.db.models import Q
from django.http import HttpResponse
from website.models import Transfer, Account, Standard
from website.views.functions.authentication import authorized
from website.views.functions.dbinterface import add_transfer, mod_transfer, del_transfer


def transfers_view(request, account):
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

        if request.method == 'POST':

            # The user wants to export the transfers
            if "export" in request.POST:

                # Date used in the file name
                date = datetime.now().strftime("%Y/%m/%d-%H-%M")
                # Creating the file and putting it in an HTTP response
                response = HttpResponse(content_type='text/csv',
                                        headers={'Content-Disposition': 'attachment; \
                                                  filename=ffts_"' + str(account).replace(" ", "_") + '_transfers_' + date + '.csv"'})

                # Setting the right GMT string for the file output (+01, -05, ...)
                gmt = str(Account.objects.all().get(user__exact=request.user, unique__exact=account).gmt)
                if gmt[0] == "-" or gmt[0] == "+":
                    if len(gmt) == 2:
                        gmt = gmt[0] + "0" + gmt[1]  # '+1' to '+01'
                else:
                    gmt = "+" + gmt  # '1' to '+1'
                    if len(gmt) == 2:
                        gmt = gmt[0] + "0" + gmt[1]  # '+1' to '+01'

                # Writting each transaction in the file
                writer = csvwriter(response)
                for trans in Transfer.objects.all().filter(Q(source__exact=account) | Q(destination__exact=account)).order_by('-date'):
                    writer.writerow([
                        acc_clean(trans.source),
                        acc_clean(trans.destination),
                        str(trans.date).replace("+00:", gmt + ":"),
                        trans.unit,
                        exp_num(trans.amount),
                        exp_num(trans.fee),
                        trans.feeUnit,
                        trans.comment
                    ])

                # Returning the file to download
                return response

            # The user wants to add a transfer
            if "add_transfer" in request.POST:
                add_transfer(
                    request,
                    False,
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
            if "modify_transfer" in request.POST:
                for tr_id in str(request.POST['id']).split(','):
                    mod_transfer(
                        request,
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
            if "delete_transfer" in request.POST:
                if authenticate(request, username=request.user.username, password=request.POST['pass']):
                    for tr_id in str(request.POST['id']).split(','):
                        del_transfer(request, tr_id)

        # Web page context data
        the_account = Account.objects.all().get(user__exact=request.user, unique__exact=account)
        transfers = Transfer.objects.all().filter(Q(source__exact=account) | Q(destination__exact=account)).order_by('-date')
        accounts = Account.objects.all().filter(user__exact=request.user).order_by('name')

        # Getting the account and the user GMT
        try:
            user_gmt = int(Standard.objects.all().get(type__exact='user_gmttime').name)
        except Standard.DoesNotExist:
            user_gmt = 0
        try:
            account_gmt = int(the_account.gmt)
        except TypeError:
            account_gmt = 0

        # Modifying the date of the transactions according to the account and user GMT
        for trans in transfers:
            if str(trans.date)[11:19] != "00:00:00":
                oldhour = int(str(trans.date)[11:13])
                newhour = oldhour + (user_gmt - account_gmt)
                if newhour > 23:
                    newhour = newhour - 24
                if oldhour < 10:
                    oldhour = str("0") + str(oldhour)
                if newhour < 10:
                    newhour = str("0") + str(abs(newhour))
                trans.date = datetime.strptime(str(trans.date)[:-6].replace(" " + str(oldhour) + ":", " " + str(newhour) + ":"), "%Y-%m-%d %H:%M:%S")

        # Web page rendering
        context = {
            'file': 'transfers',
            'title': f"Transfers - {the_account.name}",
            'transfers': transfers,
            'account_': the_account,
            'account': account,
            'accounts': accounts,
        }
        return render(request, "transfers.html", context)

    # Account + User did not matched
    return redirect('website-accounts')


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
    return number.quantize(Decimal(1)) if number == number.to_integral() else number.normalize()
