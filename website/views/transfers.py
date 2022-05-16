import csv, decimal
from datetime import datetime
import website.views.functions.authentication as auth
from website.models import Transfer, Account
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
                response = HttpResponse(content_type = 'text/csv', headers = {'Content-Disposition': 'attachment; filename=ffts_"' + str(account).replace(" ","_") + '_transactions_' + date + '.csv"'})
                writer = csv.writer(response)
                
                for t in Transfer.objects.all().filter(Q(source__exact=account) | Q(destination__exact=account)).order_by('-date'):
                    writer.writerow([exp_acc(t.source), exp_acc(t.destination), t.date, t.unit, exp_num(t.amount), exp_num(t.fee), t.feeType, t.comment])

                return response

            if "add_transfer" in request.POST:
                Transfer.objects.create(source=Account.objects.all().get(unique__exact=request.POST['source']), destination=Account.objects.all().get(unique__exact=request.POST['destination']), date=request.POST['date'], unit=request.POST['unit'], amount=request.POST['amount'], fee=request.POST['fee'], feeType=request.POST['feetype'], comment=request.POST['comment'])

            if "modify_transfer" in request.POST:
                if Transfer.objects.all().filter(Q(id__exact=request.POST['id']), Q(source__exact=account) | Q(destination__exact=account)).exists():
                    updated_transf = Transfer.objects.all().get(id__exact=request.POST['id'])
                    if len(request.POST['source']) > 0: updated_transf.source = Account.objects.all().get(unique__exact=request.POST['source'])
                    if len(request.POST['destination']) > 0: updated_transf.destination = Account.objects.all().get(unique__exact=request.POST['destination'])
                    if len(request.POST['date']) > 0: updated_transf.date = request.POST['date']
                    if len(request.POST['unit']) > 0: updated_transf.unit = request.POST['unit']
                    if len(request.POST['amount']) > 0: updated_transf.amount = request.POST['amount']
                    if len(request.POST['fee']) > 0: updated_transf.fee = request.POST['fee']
                    if len(request.POST['feetype']) > 0: updated_transf.feeType = request.POST['feetype']
                    if len(request.POST['comment']) > 0: updated_transf.comment = request.POST['comment']
                    updated_transf.save()

            if "delete_transfer" in request.POST:
                if authenticate(request, username=request.user.username, password=request.POST['pass']):
                    for id in str(request.POST['id']).split(','):
                        Transfer.objects.all().filter(Q(id__exact=id), Q(source__exact=account) | Q(destination__exact=account)).delete()

        the_account = Account.objects.all().get(user__exact=request.user, unique__exact=account)
        transfers = Transfer.objects.all().filter(Q(source__exact=account) | Q(destination__exact=account)).order_by('-date')
        accounts = Account.objects.all().filter(user__exact=request.user).order_by('name')

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