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

    if not authorized(request):
        return redirect('website-login')

    if Account.objects.all().filter(user__exact=request.user, unique__exact=account).exists():

        if request.method == 'POST':

            if "export" in request.POST:

                date = datetime.now().strftime("%Y/%m/%d-%H-%M")
                response = HttpResponse(content_type='text/csv',
                                        headers={'Content-Disposition': 'attachment; \
                                                  filename=ffts_"' + str(account).replace(" ", "_") + '_transfers_' + date + '.csv"'})
                writer = csvwriter(response)

                gmt = str(Account.objects.all().get(user__exact=request.user, unique__exact=account).gmt)
                if gmt[0] == "-" or gmt[0] == "+":
                    if len(gmt) == 2:
                        gmt = gmt[0] + "0" + gmt[1]
                else:
                    gmt = "+" + gmt
                    if len(gmt) == 2:
                        gmt = gmt[0] + "0" + gmt[1]

                for trans in Transfer.objects.all().filter(Q(source__exact=account) | Q(destination__exact=account)).order_by('-date'):
                    writer.writerow([
                        exp_acc(trans.source),
                        exp_acc(trans.destination),
                        str(trans.date).replace("+00:", gmt + ":"),
                        trans.unit,
                        exp_num(trans.amount),
                        exp_num(trans.fee),
                        trans.feeUnit,
                        trans.comment
                    ])
                return response

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

            if "delete_transfer" in request.POST:
                if authenticate(request, username=request.user.username, password=request.POST['pass']):
                    for tr_id in str(request.POST['id']).split(','):
                        del_transfer(request, tr_id)

        the_account = Account.objects.all().get(user__exact=request.user, unique__exact=account)
        transfers = Transfer.objects.all().filter(Q(source__exact=account) | Q(destination__exact=account)).order_by('-date')
        accounts = Account.objects.all().filter(user__exact=request.user).order_by('name')

        try:
            mygmt = int(Standard.objects.all().get(type__exact='MyGMTtime').name)
        except Standard.DoesNotExist:
            mygmt = 0
        try:
            accgmt = int(the_account.gmt)
        except TypeError:
            accgmt = 0

        for trans in transfers:
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
            'page': 'transfers',
            'transfers': transfers,
            'account_': the_account,
            'account': account,
            'accounts': accounts,
        }
        return render(request, "transfers.html", context)

    else:
        return redirect('website-accounts')


def exp_acc(account):
    return str(account).replace("Account object (", "")[:-1]


def exp_num(number):
    return number.quantize(Decimal(1)) if number == number.to_integral() else number.normalize()
