import csv, decimal
from datetime import datetime
import website.views.functions.authentication as auth
from django.shortcuts import render, redirect
from website.models import Transaction, Account, Standard
from django.contrib.auth import authenticate
from django.http import HttpResponse
import website.views.functions.dbinterface as dbi

def transactions_view(request, account):

    if not auth.amIauthorized(request):
        return redirect('website-login')

    if Account.objects.all().filter(user__exact=request.user, unique__exact=account).exists():

        if request.method == 'POST':

            if "export" in request.POST:

                date = datetime.now().strftime("%Y/%m/%d-%H-%M")
                response = HttpResponse(content_type = 'text/csv', headers = {'Content-Disposition': 'attachment; filename=ffts_"' + str(account).replace(" ","_") + '_transactions_' + date + '.csv"'})
                writer = csv.writer(response)

                gmt = str(Account.objects.all().get(user__exact=request.user, unique__exact=account).gmt)
                if gmt[0] == "-" or gmt[0] == "+":
                    if len(gmt) == 2:
                        gmt = gmt[0] + "0" + gmt[1]
                else:
                    gmt = "+" + gmt
                    if len(gmt) == 2:
                        gmt = gmt[0] + "0" + gmt[1]
                
                for t in Transaction.objects.all().filter(account__exact=account).order_by('-date'):
                    writer.writerow([exp_acc(t.account), t.market, t.type, str(t.date).replace("+00:",gmt + ":"), t.input, t.output, exp_num(t.amountIn), exp_num(t.amountOut), exp_num(t.price), exp_num(t.fee), t.feeUnit, t.comment])

                return response

            if "add_transaction" in request.POST:
                dbi.addTransaction(request, False, account, request.POST['market'], request.POST['type'], request.POST['date'], request.POST['input'], request.POST['output'], 
                    request.POST['amountin'], request.POST['amountout'], request.POST['price'], request.POST['fee'], request.POST['feeunit'], request.POST['comment'])

            if "modify_transaction" in request.POST:
                for id in str(request.POST['id']).split(','):
                    dbi.modTransaction(request, id, request.POST['market'], request.POST['type'], request.POST['date'], request.POST['input'], request.POST['output'], 
                        request.POST['amountin'], request.POST['amountout'], request.POST['price'], request.POST['fee'], request.POST['feeunit'], request.POST['comment'])

            if "delete_transaction" in request.POST:
                if authenticate(request, username=request.user.username, password=request.POST['pass']):
                    for id in str(request.POST['id']).split(','):
                        dbi.delTransaction(request, id)
                    

        the_account = Account.objects.all().get(user__exact=request.user, unique__exact=account)
        transactions = Transaction.objects.all().filter(account__exact=account).order_by('-date','type','input','output')
        tr_types = Standard.objects.all().filter(type__exact='TransactionType').order_by('name')

        try: mygmt = int(Standard.objects.all().get(type__exact='MyGMTtime').name)
        except: mygmt = 0
        try: accgmt = int(the_account.gmt)
        except: accgmt = 0
        
        for t in transactions:
            if str(t.date)[11:19] != "00:00:00":
                hour = int(str(t.date)[11:13])
                newhour = hour + (mygmt - accgmt)
                if newhour > 23: newhour = newhour - 24
                if hour < 10: hour = str("0") + str(hour)
                if newhour < 10: newhour = str("0") + str(newhour)
                t.date = datetime.strptime(str(t.date)[:-6].replace(" " + str(hour) + ":", " " + str(newhour) + ":"), "%Y-%m-%d %H:%M:%S")

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

def exp_acc(a):
    return str(a).replace("Account object (","")[:-1]

def exp_num(n):
    return n.quantize(decimal.Decimal(1)) if n == n.to_integral() else n.normalize()