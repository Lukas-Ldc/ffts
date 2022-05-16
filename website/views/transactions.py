import csv, decimal
from datetime import datetime
import website.views.functions.authentication as auth
from django.shortcuts import render, redirect
from website.models import Transaction, Account, Standard
from django.contrib.auth import authenticate
from django.http import HttpResponse

def transactions_view(request, account):

    if not auth.amIauthorized(request):
        return redirect('website-login')

    if Account.objects.all().filter(user__exact=request.user, unique__exact=account).exists():

        if request.method == 'POST':

            if "export" in request.POST:

                date = datetime.now().strftime("%Y/%m/%d-%H-%M")
                response = HttpResponse(content_type = 'text/csv', headers = {'Content-Disposition': 'attachment; filename=ffts_"' + str(account).replace(" ","_") + '_transactions_' + date + '.csv"'})
                writer = csv.writer(response)
                
                for t in Transaction.objects.all().filter(account__exact=account).order_by('-date'):
                    writer.writerow([exp_acc(t.account), t.market, t.type, t.date, t.input, t.output, exp_num(t.amountIn), exp_num(t.amountOut), exp_num(t.price), exp_num(t.fee), t.feeType, t.comment])

                return response

            if "add_transaction" in request.POST and trans_type_checker(request.POST['type']):
                Transaction.objects.create(account=Account.objects.all().get(user__exact=request.user, unique__exact=account), market=request.POST['market'], type=request.POST['type'], date=request.POST['date'], input=request.POST['input'], output=request.POST['output'], amountIn=request.POST['amountin'], amountOut=request.POST['amountout'], price=request.POST['price'], fee=request.POST['fee'], feeType=request.POST['feetype'], comment=request.POST['comment'])

            if "modify_transaction" in request.POST:
                if Transaction.objects.all().filter(id__exact=request.POST['id'], account__exact=account).exists():
                    updated_transac = Transaction.objects.all().get(id__exact=request.POST['id'], account__exact=account)
                    if len(request.POST['market']) > 0: updated_transac.market = request.POST['market']
                    if trans_type_checker(request.POST['type']): updated_transac.type = request.POST['type']
                    if len(request.POST['date']) > 0: updated_transac.date = request.POST['date']
                    if len(request.POST['input']) > 0: updated_transac.input = request.POST['input']
                    if len(request.POST['output']) > 0: updated_transac.output = request.POST['output']
                    if len(request.POST['amountin']) > 0: updated_transac.amountIn = request.POST['amountin']
                    if len(request.POST['amountout']) > 0: updated_transac.amountOut = request.POST['amountout']
                    if len(request.POST['price']) > 0: updated_transac.price = request.POST['price']
                    if len(request.POST['fee']) > 0: updated_transac.fee = request.POST['fee']
                    if len(request.POST['feetype']) > 0: updated_transac.feeType = request.POST['feetype']
                    if len(request.POST['comment']) > 0: updated_transac.comment = request.POST['comment']
                    updated_transac.save()

            if "delete_transaction" in request.POST:
                if authenticate(request, username=request.user.username, password=request.POST['pass']):
                    for id in str(request.POST['id']).split(','):
                        Transaction.objects.all().filter(id__exact=id, account__exact=account).delete()

        the_account = Account.objects.all().get(user__exact=request.user, unique__exact=account)
        transactions = Transaction.objects.all().filter(account__exact=account).order_by('-date','type','input','output')
        tr_types = Standard.objects.all().filter(type__exact='TransactionType').order_by('name')

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

#Verify if the type given by the user is in the database
def trans_type_checker(t):
    if Standard.objects.all().filter(type__exact='TransactionType', name__exact=t).exists():
        return True
    else:
        return False

def exp_acc(a):
    return str(a).replace("Account object (","")[:-1]

def exp_num(n):
    return n.quantize(decimal.Decimal(1)) if n == n.to_integral() else n.normalize()