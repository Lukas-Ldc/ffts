from decimal import DivisionByZero, InvalidOperation
from django.shortcuts import render, redirect
from django.db.models import Q
from website.models import Transfer, Transaction, Account
from website.views.functions.authentication import authorized


def account_view(request, name):
    """The view for the account page

    Args:
        request (HttpRequest): The request for the account page

    Returns:
        HttpResponse: The account page
    """

    if not authorized(request):
        return redirect('website-login')

    # If the account belongs to the user who made the request
    if Account.objects.all().filter(user__exact=request.user, unique__exact=name).exists():
        # FIXME: Account units total not always correct

        account = Account.objects.all().get(user__exact=request.user, unique__exact=name)
        transfers = Transfer.objects.all().filter(Q(source__exact=name) | Q(destination__exact=name))
        transactions = Transaction.objects.all().filter(account__exact=name).order_by('input', 'output')
        acc_units = str(account.unit).split(",")

        # [data] :                (0) : UNIT
        #       Transactions part (1) : ACC_UNIT | VOL_IN | VOL_OUT | VOL_ACC_UNIT_IN | VOL_ACC_UNIT_OUT | VOL_FEE | VOL_FEE_ACC_UNIT
        #       Transfers part    (2) : VOL_IN | VOL_OUT | VOL_FEE_IN | VOL_FEE_OUT
        data = []
        overview = []
        temp = []
        acc = []

        # Data creation by finding all units
        for unit in transfers.values('unit').order_by('unit').distinct():
            data.append([str(unit)[:-2][10:], '', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

        for unit in transactions.values('input').order_by('input').distinct():
            found = False
            for ok_unit in data:
                if str(unit)[:-2][11:] == ok_unit[0]:
                    found = True
                    break
            if not found:
                data.append([str(unit)[:-2][11:], '', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

        for unit in transactions.values('output').order_by('output').distinct():
            found = False
            for ok_unit in data:
                if str(unit)[:-2][12:] == ok_unit[0]:
                    found = True
                    break
            if not found:
                data.append([str(unit)[:-2][12:], '', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

        data = sorted(data, key=lambda x: x[0])

        # Adding Transactions data
        for trans in transactions:
            for unit in data:

                if trans.input == unit[0]:
                    unit[3] = unit[3] + trans.amountIn
                    if trans.output in acc_units:
                        if len(unit[1]) < 1:
                            unit[1] = trans.output
                            if unit[0] in acc_units:
                                unit[1] = unit[0]
                        if unit[1] == trans.output:
                            unit[5] = unit[5] + trans.amountOut
                    if trans.feeUnit == unit[1]:
                        unit[7] = unit[7] + trans.fee

                elif trans.output == unit[0]:
                    unit[2] = unit[2] + trans.amountOut
                    if trans.input in acc_units:
                        if len(unit[1]) < 1:
                            unit[1] = trans.input
                            if unit[0] in acc_units:
                                unit[1] = unit[0]
                        if unit[1] == trans.input:
                            unit[4] = unit[4] + trans.amountIn
                    if trans.feeUnit == unit[1]:
                        unit[7] = unit[7] + trans.fee

                if trans.feeUnit == unit[0]:
                    unit[6] = unit[6] + trans.fee

        # Adding Transfers data
        for trans in transfers:
            for unit in data:

                if trans.unit == unit[0]:
                    if acc_clean(trans.source) == account.unique:
                        unit[9] = unit[9] + trans.amount
                    elif acc_clean(trans.destination) == account.unique:
                        unit[8] = unit[8] + trans.amount

                if trans.feeUnit == unit[0]:
                    if acc_clean(trans.source) == account.unique:
                        unit[11] = unit[11] + trans.fee
                    elif acc_clean(trans.destination) == account.unique:
                        unit[10] = unit[10] + trans.fee

        # Assets Overview Calculs
        for unit in data:
            # if unit[2] > 0 or unit[3] > 0:

            amount = (unit[2] - unit[3] - unit[6]) + (unit[8] - unit[9] - unit[11])
            p_and_l = unit[5] - unit[4] - unit[7]

            try:
                avg_u_in = unit[4] / unit[2]
            except (TypeError, ZeroDivisionError):
                avg_u_in = 0

            try:
                avg_u_out = unit[5] / unit[3]
            except (TypeError, ZeroDivisionError):
                avg_u_out = 0

            try:
                perf = (unit[5] / unit[4]) * 100 - 100
            except (TypeError, ZeroDivisionError, DivisionByZero, InvalidOperation):
                perf = 0

            if unit[0] in acc_units:
                perf = avg_u_in = avg_u_out = 0
                p_and_l = unit[2] - unit[3] - unit[6]

            if unit[0] in acc_units:
                acc.append([unit[0], unit[1], amount, perf, p_and_l, avg_u_in, avg_u_out, 1])
            elif amount == 0:
                temp.append([unit[0], unit[1], amount, perf, p_and_l, avg_u_in, avg_u_out, 0])
            else:
                overview.append([unit[0], unit[1], amount, perf, p_and_l, avg_u_in, avg_u_out, 0])

        overview = acc + overview + temp

        # Web page rendering
        context = {
            'page': 'account',
            'account': account,
            'data': data,
            'overview': overview,
        }
        return render(request, "account.html", context)

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
    return str(account)[:-1].replace("Account object (", "")
