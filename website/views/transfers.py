import csv, decimal
from datetime import datetime
import website.views.functions.authentication as auth
from website.models import Transfer, Account, Standard
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.db.models import Q
from django.http import HttpResponse


def transfers_view(request, account):

    if not auth.amIauthorized(request):
        return redirect('website-login')

    if Account.objects.all().filter(user__exact=request.user, unique__exact=account).exists():

        if request.method == 'POST':

            if "export" in request.POST:

                date = datetime.now().strftime("%Y/%m/%d-%H-%M")
                response = HttpResponse(content_type = 'text/csv', headers = {'Content-Disposition': 'attachment; filename=ffts_"' + str(account).replace(" ","_") + '_transfers_' + date + '.csv"'})
                writer = csv.writer(response)

                gmt = str(Account.objects.all().get(user__exact=request.user, unique__exact=account).gmt)
                if gmt[0] == "-" or gmt[0] == "+":
                    if len(gmt) == 2:
                        gmt = gmt[0] + "0" + gmt[1]
                else:
                    gmt = "+" + gmt
                    if len(gmt) == 2:
                        gmt = gmt[0] + "0" + gmt[1]
                
                for t in Transfer.objects.all().filter(Q(source__exact=account) | Q(destination__exact=account)).order_by('-date'):
                    writer.writerow([exp_acc(t.source), exp_acc(t.destination), str(t.date).replace("+00:",gmt + ":"), t.unit, exp_num(t.amount), exp_num(t.fee), t.feeUnit, t.comment])

                return response

            if "add_transfer" in request.POST:
                Transfer.objects.create(
                    source=Account.objects.all().get(unique__exact=request.POST['source']), 
                    destination=Account.objects.all().get(unique__exact=request.POST['destination']), 
                    date=request.POST['date'], 
                    unit=request.POST['unit'], 
                    amount=request.POST['amount'], 
                    fee=request.POST['fee'], 
                    feeUnit=request.POST['feeunit'], 
                    comment=request.POST['comment']
                )

            if "modify_transfer" in request.POST:
                if Transfer.objects.all().filter(Q(id__exact=request.POST['id']), Q(source__exact=account) | Q(destination__exact=account)).exists():
                    updated_transf = Transfer.objects.all().get(id__exact=request.POST['id'])
                    if len(request.POST['source']) > 0: updated_transf.source = Account.objects.all().get(unique__exact=request.POST['source'])
                    if len(request.POST['destination']) > 0: updated_transf.destination = Account.objects.all().get(unique__exact=request.POST['destination'])
                    if len(request.POST['date']) > 0: updated_transf.date = request.POST['date']
                    if len(request.POST['unit']) > 0: updated_transf.unit = request.POST['unit']
                    if len(request.POST['amount']) > 0: updated_transf.amount = request.POST['amount']
                    if len(request.POST['fee']) > 0: updated_transf.fee = request.POST['fee']
                    if len(request.POST['feeunit']) > 0: updated_transf.feeUnit = request.POST['feeunit']
                    if len(request.POST['comment']) > 0: updated_transf.comment = request.POST['comment']
                    updated_transf.save()

            if "delete_transfer" in request.POST:
                if authenticate(request, username=request.user.username, password=request.POST['pass']):
                    for id in str(request.POST['id']).split(','):
                        Transfer.objects.all().filter(Q(id__exact=id), Q(source__exact=account) | Q(destination__exact=account)).delete()

        the_account = Account.objects.all().get(user__exact=request.user, unique__exact=account)
        transfers = Transfer.objects.all().filter(Q(source__exact=account) | Q(destination__exact=account)).order_by('-date')
        accounts = Account.objects.all().filter(user__exact=request.user).order_by('name')

        try: mygmt = int(Standard.objects.all().get(type__exact='MyGMTtime').name)
        except: mygmt = 0
        try: accgmt = int(the_account.gmt)
        except: accgmt = 0
        
        for t in transfers:
            if str(t.date)[11:19] != "00:00:00":
                hour = int(str(t.date)[11:13])
                newhour = hour + (mygmt - accgmt)
                if newhour > 23: newhour = newhour - 24
                if hour < 10: hour = str("0") + str(hour)
                if newhour < 10: newhour = str("0") + str(newhour)
                t.date = datetime.strptime(str(t.date)[:-6].replace(" " + str(hour) + ":", " " + str(newhour) + ":"), "%Y-%m-%d %H:%M:%S")

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

def exp_acc(a):
    return str(a).replace("Account object (","")[:-1]

def exp_num(n):
    return n.quantize(decimal.Decimal(1)) if n == n.to_integral() else n.normalize()