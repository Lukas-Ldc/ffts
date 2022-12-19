from csv import writer as csvwriter
from decimal import Decimal
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.http import HttpResponse
from website.models import Transaction, Account, Standard
from website.views.functions.authentication import authorized
from website.views.functions.dbinterface import add_transaction, mod_transaction, del_transaction


def transactions_view(request, account):

    if not authorized(request):
        return redirect('website-login')

    if Account.objects.all().filter(user__exact=request.user, unique__exact=account).exists():

        if request.method == 'POST':

            if "export" in request.POST:

                date = datetime.now().strftime("%Y/%m/%d-%H-%M")
                response = HttpResponse(content_type='text/csv',
                                        headers={'Content-Disposition': 'attachment; \
                                                  filename=ffts_"' + str(account).replace(" ", "_") + '_transactions_' + date + '.csv"'})
                writer = csvwriter(response)

                gmt = str(Account.objects.all().get(user__exact=request.user, unique__exact=account).gmt)
                if gmt[0] == "-" or gmt[0] == "+":
                    if len(gmt) == 2:
                        gmt = gmt[0] + "0" + gmt[1]
                else:
                    gmt = "+" + gmt
                    if len(gmt) == 2:
                        gmt = gmt[0] + "0" + gmt[1]

                for trans in Transaction.objects.all().filter(account__exact=account).order_by('-date'):
                    writer.writerow([
                        exp_acc(trans.account),
                        trans.market,
                        trans.type,
                        str(trans.date).replace("+00:", gmt + ":"),
                        trans.input,
                        trans.output,
                        exp_num(trans.amountIn),
                        exp_num(trans.amountOut),
                        exp_num(trans.price),
                        exp_num(trans.fee),
                        trans.feeUnit,
                        trans.comment
                    ])
                return response

            if "add_transaction" in request.POST:
                add_transaction(
                    request,
                    False,
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

            if "modify_transaction" in request.POST:
                for tr_id in str(request.POST['id']).split(','):
                    mod_transaction(
                        request,
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

            if "delete_transaction" in request.POST:
                if authenticate(request, username=request.user.username, password=request.POST['pass']):
                    for tr_id in str(request.POST['id']).split(','):
                        del_transaction(request, tr_id)

        the_account = Account.objects.all().get(user__exact=request.user, unique__exact=account)
        transactions = Transaction.objects.all().filter(account__exact=account).order_by('-date', 'type', 'input', 'output')
        tr_types = Standard.objects.all().filter(type__exact='TransactionType').order_by('name')

        try:
            mygmt = int(Standard.objects.all().get(type__exact='MyGMTtime').name)
        except Standard.DoesNotExist:
            mygmt = 0
        try:
            accgmt = int(the_account.gmt)
        except TypeError:
            accgmt = 0

        for trans in transactions:
            if str(trans.date)[11:19] != "00:00:00":
                hour = int(str(trans.date)[11:13])
                newhour = hour + (mygmt - accgmt)
                if newhour > 23:
                    newhour = newhour - 24
                if hour < 10:
                    hour = str("0") + str(hour)
                if newhour < 10:
                    newhour = str("0") + str(abs(newhour))
                trans.date = datetime.strptime(str(trans.date)[:-6].replace(" " + str(hour) + ":", " " + str(newhour) + ":"), "%Y-%m-%d %H:%M:%S")

        context = {
            'page': 'transactions',
            'transactions': transactions,
            'account_': the_account,
            'types': tr_types,
            'account': account,
        }
        return render(request, "transactions.html", context)

    else:
        return redirect('website-accounts')


def exp_acc(account):
    return str(account).replace("Account object (", "")[:-1]


def exp_num(number):
    return number.quantize(Decimal(1)) if number == number.to_integral() else number.normalize()
