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

        #Assets Overview
        overv_transa = []
        overv_calc = []

        #--Transactions part
        transa_usdt = transactions.filter(Q(input__exact = account.unit) | Q(output__exact = account.unit))
        for u in unitFinder(True, transa_usdt):
            temp = []
            #UNIT TOTALIN TOTALOUT USDTIN USDTOUT FEE
            for i in [u, 0, 0, 0, 0, 0]:
                temp.append(i)
            overv_transa.append(temp)
        
        for tr in transa_usdt:
            feeCalc = feeCalculator(True, tr, account)
            for t in overv_transa:
                if t[0] == tr.input:
                    t[1] = t[1] + feeCalc[0]
                    t[3] = t[3] + feeCalc[1]
                    t[5] = t[5] + feeCalc[2]
                if t[0] == tr.output:
                    t[2] = t[2] + feeCalc[1]
                    t[4] = t[4] + feeCalc[0]
                    t[5] = t[5] + feeCalc[3]

        for t in overv_transa:
            amount = t[2] - t[1] - t[5]
            try: avg_for_in = t[3] / t[1]
            except: avg_for_in = t[3]
            try: avg_for_out = t[4] / t[2]
            except: avg_for_out = t[4]
            try: perf = (t[3] / t[4]) * 100 - 100
            except: perf = 0
            if t[0] == account.unit: perf = avg_for_out = avg_for_in = 0
            temp = []
            for a in [t[0], amount, perf, avg_for_out, avg_for_in]:
                temp.append(a)
            overv_calc.append(temp)

        #--Transfers part
        for tr in transfers:
            for t in overv_calc:
                if tr.unit == t[0]:
                    if tr.source == account.unique:
                        t[1] = t[1] - tr.amount
                    else:
                        t[1] = t[1] + tr.amount

        #Transactions Overview
        transa_calc = []
        for u in unitFinder(True, transactions):
            temp = []
            #UNIT IN OUT FEE
            for i in [u, 0, 0, 0]:
                temp.append(i)
            transa_calc.append(temp)

        for tr in transactions:
            feeCalc = feeCalculator(True, tr, account)
            for t in transa_calc:
                if t[0] == tr.input:
                    t[1] = t[1] + feeCalc[0]
                    t[3] = t[3] + feeCalc[2]
                if t[0] == tr.output:
                    t[2] = t[2] + feeCalc[1]
                    t[3] = t[3] + feeCalc[3]

        #Transfers Overview
        transf_calc_temp = []
        transf_calc = []

        for u in unitFinder(False, transfers):
            temp = []
            for i in [u, "Input", 0, 0]:
                temp.append(i)
            transf_calc_temp.append(temp)
            temp = []
            for i in [u, "Output", 0, 0]:
                temp.append(i)
            transf_calc_temp.append(temp)

        for tr in transfers:
            feeCalc = feeCalculator(False, tr, account)
            for t in transf_calc_temp:
                if (t[0] == tr.unit and t[1] == "Output" and ac_clean(tr.source) == name) or (t[0] == tr.unit and t[1] == "Input" and ac_clean(tr.destination) == name):
                    t[2] = t[2] + feeCalc[0]
                    t[3] = t[3] + feeCalc[1]
                    break
        
        for f in transf_calc_temp:
            if f[2] != 0:
                temp = []
                for a in f:
                    temp.append(a)
                transf_calc.append(temp)

        #Fees Overview
        fees_calc_temp = []
        fees_calc = []

        for u in overv_calc:
            temp = []
            #UNIT FEE
            for i in [u[0], 0]:
                temp.append(i)
            fees_calc_temp.append(temp)

        for tr in transactions:
            feeCalc = feeCalculator(True, tr, account)
            for t in fees_calc_temp:
                if t[0] == tr.input:
                    t[1] = t[1] + feeCalc[2]
                if t[0] == tr.output:
                    t[1] = t[1] + feeCalc[3]
        
        for tr in transfers:
            feeCalc = feeCalculator(False, tr, account)
            for t in fees_calc_temp:
                if t[0] == tr.unit:
                    t[1] = t[1] + feeCalc[1]

        for f in fees_calc_temp:
            if f[1] != 0:
                temp = []
                for a in f:
                    temp.append(a)
                fees_calc.append(temp)

        context = {
            'page': 'account',
            'account': account,
            'transfers': transf_calc,
            'transactions': transa_calc,
            'overview': overv_calc,
            'fees': fees_calc,
        }
        return render(request, "account.html", context)
    
    else:
        return redirect('website-accounts')


def ac_clean(a):
    return str(a)[:-1].replace("Account object (", "")


def ft_clean(f):
    if len(str(f).replace(" ", "")) > 0:
        if f[0] == "-" or f[0] == "+":
            return [f[1:],f[0]]
        else:
            return [f, None]
    else:
        return [None, None]


def feeCalculator(isTransa, info, acc):
    fT = ft_clean(info.feeType)
    if isTransa:
        if fT[1] == "-":
            if fT[0] == info.input:
                return [info.amountIn - info.fee, info.amountOut, info.fee, 0]
            elif fT[0] == info.output:
                return [info.amountIn, info.amountOut - info.fee, 0, info.fee]
        else:
            if fT[0] == info.input or fT[0] is None and acc.unit == info.input:
                return [info.amountIn, info.amountOut, info.fee, 0]
            elif fT[0] == info.output or fT[0] is None and acc.unit == info.output:
                return [info.amountIn, info.amountOut, 0, info.fee]
            else:
                return [info.amountIn, info.amountOut, 0, 0]
    else:
        if fT[1] == "-" and fT[0] == info.unit:
            return [info.amount - info.fee, info.fee]
        elif fT[0] == info.unit or fT[0] is None and acc.unit == info.unit:
            return [info.amount, info.fee]
        else:
            return [info.amount, 0]

def unitFinder(isTransa, query):
    units = []
    if isTransa:
        for u in query.values('input').order_by('input').distinct():
            units.append(str(u)[:-2][11:])
        for u in query.values('output').order_by('output').distinct():
            isIn = False
            for v in units:
                if str(u)[:-2][12:] == v:
                    isIn = True
                    break
            if not isIn:
                units.append(str(u)[:-2][12:])
    else:
        for u in query.values('unit').order_by('unit').distinct():
            units.append(str(u)[:-2][10:])
    units.sort()
    return units
