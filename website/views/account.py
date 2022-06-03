import website.views.functions.authentication as auth
from django.shortcuts import render, redirect
from website.models import Transfer, Transaction, Account
from django.db.models import Q

def account_view(request, name):

    if not auth.amIauthorized(request):
        return redirect('website-login')

    if Account.objects.all().filter(user__exact=request.user, unique__exact=name).exists():

        account = Account.objects.all().get(user__exact=request.user, unique__exact=name)
        transfers = Transfer.objects.all().filter(Q(source__exact=name) | Q(destination__exact=name))
        transactions = Transaction.objects.all().filter(account__exact=name).order_by('input','output')
        acc_units = str(account.unit).split(",")

        # [data] :                (0) : UNIT
        #       Transactions part (1) : ACC_UNIT | VOL_IN | VOL_OUT | VOL_ACC_UNIT_IN | VOL_ACC_UNIT_OUT | VOL_FEE | VOL_FEE_ACC_UNIT
        #       Transfers part    (2) : VOL_IN | VOL_OUT | VOL_FEE_IN | VOL_FEE_OUT
        data = []
        overview = []

        #Data creation by finding all units
        for t in transfers.values('unit').order_by('unit').distinct():
            data.append([str(t)[:-2][10:],'',0,0,0,0,0,0,0,0,0,0])

        for t in transactions.values('input').order_by('input').distinct():
            iSin = False
            for u in data:
                if str(t)[:-2][11:] == u[0]:
                    iSin = True
                    break
            if not iSin:
                data.append([str(t)[:-2][11:],'',0,0,0,0,0,0,0,0,0,0])

        for t in transactions.values('output').order_by('output').distinct():
            iSin = False
            for u in data:
                if str(t)[:-2][12:] == u[0]:
                    iSin = True
                    break
            if not iSin:
                data.append([str(t)[:-2][12:],'',0,0,0,0,0,0,0,0,0,0])

        data = sorted(data, key=lambda x:x[0])

        #Adding Transactions data
        for t in transactions:
            for d in data:

                if t.input == d[0]:
                    d[3] = d[3] + t.amountIn
                    if t.output in acc_units:
                        if len(d[1]) < 1:
                            d[1] = t.output
                            if d[0] in acc_units:
                                d[1] = d[0]
                        if d[1] == t.output:
                            d[5] = d[5] + t.amountOut
                    if t.feeUnit == d[1]:
                        d[7] = d[7] + t.fee

                elif t.output == d[0]:
                    d[2] = d[2] + t.amountOut
                    if t.input in acc_units:
                        if len(d[1]) < 1:
                            d[1] = t.input
                            if d[0] in acc_units:
                                d[1] = d[0]
                        if d[1] == t.input:
                            d[4] = d[4] + t.amountIn
                    if t.feeUnit == d[1]:
                        d[7] = d[7] + t.fee

                if t.feeUnit == d[0]:
                    d[6] = d[6] + t.fee

        #Adding Transfers data
        for t in transfers:
            for d in data:

                if t.unit == d[0]:
                    if ac_clean(t.source) == account.unique:
                        d[9] = d[9] + t.amount
                    elif ac_clean(t.destination) == account.unique:
                        d[8] = d[8] + t.amount

                if t.feeUnit == d[0]:
                    if ac_clean(t.source) == account.unique:
                        d[11] = d[11] + t.fee
                    elif ac_clean(t.destination) == account.unique:
                        d[10] = d[10] + t.fee

        #Assets Overview Calculs
        for d in data:
            if d[2] > 0 or d[3] > 0:

                amount = (d[2] - d[3] - d[6]) + (d[8] - d[9] - d[11])
                pAndL = d[5] - d[4] - d[7]
                try: avg_u_in = d[4] / d[2]
                except: avg_u_in = 0
                try: avg_u_out = d[5] / d[3]
                except: avg_u_out = 0
                try: perf = (d[5] / d[4]) *100 -100
                except: perf = 0

                if d[0] in acc_units:
                    perf = avg_u_in = avg_u_out = 0
                    pAndL = d[2] - d[3] - d[6]

                overview.append([d[0],d[1],amount,perf,pAndL,avg_u_in,avg_u_out])    

        context = {
            'page': 'account',
            'account': account,
            'data': data,
            'overview': overview,
        }
        return render(request, "account.html", context)
    
    else:
        return redirect('website-accounts')


def ac_clean(a):
    return str(a)[:-1].replace("Account object (", "")
