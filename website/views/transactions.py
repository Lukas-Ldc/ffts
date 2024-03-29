from csv import writer as csvwriter
from datetime import datetime
from zoneinfo import ZoneInfo, available_timezones
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.http import HttpResponse, HttpRequest
from django.contrib.auth.models import User
from website.models import Transaction, Account, Standard
from website.views.functions.authentication import authorized
from website.views.functions.data_functions import float_0_cleaner
from website.views.functions.dbinterface import add_transaction, mod_transaction, del_transaction


def transactions_view(request: HttpRequest, account: str):
    """The view for the transaction page

    Args:
        request (HttpRequest): The request for the transaction page
        account (str): The name of the account

    Returns:
        HttpResponse: The transaction page or the export of the transactions
    """

    if not authorized(request):
        return redirect('website-login')

    # If the account belongs to the user who made the request
    if Account.objects.all().filter(user__exact=request.user, unique__exact=account).exists():

        if request.method == "POST":

            # The user wants to export the transactions
            if "export" in request.POST.keys():
                return transactions_export(account, request)

            # The user wants to add a transaction
            if "add_transaction" in request.POST.keys():
                add_transaction(
                    request,
                    False,
                    False,
                    request.POST['timezone'],
                    account,
                    request.POST['market'],
                    request.POST['type'],
                    request.POST['date'],
                    request.POST['input'],
                    request.POST['output'],
                    request.POST['amountin'],
                    request.POST['amountout'],
                    request.POST['price'],
                    request.POST['fee'],
                    request.POST['feeunit'],
                    request.POST['comment']
                )

            # The user wants to modify transactions
            if "modify_transaction" in request.POST.keys():
                for tr_id in str(request.POST['id']).split(','):
                    mod_transaction(
                        request,
                        False,
                        request.POST['timezone'],
                        tr_id,
                        request.POST['market'],
                        request.POST['type'],
                        request.POST['date'],
                        request.POST['input'],
                        request.POST['output'],
                        request.POST['amountin'],
                        request.POST['amountout'],
                        request.POST['price'],
                        request.POST['fee'],
                        request.POST['feeunit'],
                        request.POST['comment']
                    )

            # The user wants to delete transactions
            if "delete_transaction" in request.POST.keys():
                if authenticate(request, username=request.user.username, password=request.POST['pass']):
                    for tr_id in str(request.POST['id']).split(','):
                        del_transaction(request, tr_id)

        # Web page context data
        the_account = Account.objects.all().get(user__exact=request.user, unique__exact=account)
        transactions = Transaction.objects.all().filter(account__exact=account).order_by('-date', 'type', 'input', 'output')
        tr_types = Standard.objects.all().filter(type__exact='TransactionType').order_by('name')

        # Web page rendering
        context = {
            'file': 'transactions',
            'title': f"Transactions - {the_account.name}",
            'transactions': transactions,
            'account': the_account,
            'types': tr_types,
            'timezones': sorted(available_timezones()),
        }
        return render(request, "transactions.html", context)

    # Account + User did not matched
    return redirect('website-accounts')


def transactions_export(account: Account, request: HttpRequest):
    """Exports in a CSV all the transactions of an account.

    Args:
        account (Account): The account linked to the transactions
        request (HttpRequest): The request made to get the export

    Returns:
        HttpResponse: The CSV file
    """
    # Date used in the file name
    date = datetime.now().strftime("%Y/%m/%d-%H-%M")
    # Creating the file and putting it in an HTTP response
    response = HttpResponse(content_type='text/csv',
                            headers={'Content-Disposition': 'attachment; \
                                        filename=ffts_"' + str(account).replace(" ", "_") + '_transactions_' + date + '.csv"'})

    # Writting each transaction in the file
    writer = csvwriter(response)
    header = [str(field).split(".")[-1].replace("_", " ").title() for field in Transaction._meta.fields]
    header.remove("Id")
    writer.writerow(header)

    for trans in Transaction.objects.all().filter(account__exact=account).order_by('-date'):
        writer.writerow([
            trans.account.unique,
            trans.market,
            trans.type,
            str(trans.date.astimezone(ZoneInfo(User.objects.get(username=request.user.username).last_name))),
            trans.input,
            trans.output,
            float_0_cleaner(trans.amount_in),
            float_0_cleaner(trans.amount_out),
            float_0_cleaner(trans.price),
            float_0_cleaner(trans.fee),
            trans.fee_unit,
            trans.comment
        ])

    # Returning the file to download
    return response
