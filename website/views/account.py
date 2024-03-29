from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.db.models import Q
from website.models import Transfer, Transaction, Account
from website.views.functions.authentication import authorized
from website.views.functions.data_functions import float_limiter, all_acc_units


def account_view(request: HttpRequest, name: str):
    """The view for the account page

    Args:
        request (HttpRequest): The request for the account page
        name (str): The name of the account

    Returns:
        HttpResponse: The account page
    """

    if not authorized(request):
        return redirect('website-login')

    # If the account belongs to the user who made the request
    if Account.objects.all().filter(user__exact=request.user, unique__exact=name).exists():

        account = Account.objects.all().get(user__exact=request.user, unique__exact=name)
        transfers = Transfer.objects.all().filter(Q(source__exact=name) | Q(destination__exact=name))
        transactions = Transaction.objects.all().filter(account__exact=name)

        volume_overview = assets_calculations(account, transfers, transactions)
        pairs_overview = pairs_calculations(account, transactions)

        # Web page rendering
        context = {
            'file': 'account',
            'title': f"Account - {account.name}",
            'account': account,
            'volume_overview': volume_overview,
            'pairs_overview': pairs_overview
        }
        return render(request, "account.html", context)

    # Account + User did not matched
    return redirect('website-accounts')


def assets_calculations(account: Account, transfers: Transfer, transactions: Transaction):
    """Assets Volume Calculations

    Args:
        account (Account): The account from which originate transfer and transactions
        transfers (Transfer): The transfers to use in the calculations
        transactions (Transaction): The transactions to use in the calculations

    Returns:
        list: A list of data for each account asset:
        [the_unit: str, total_amount: float, tt_tr_in: float, tt_tr_out: float, tt_tf_in: float, tt_tf_out: float, tt_fee: float, is_acc_unit: bool]
    """
    volume_overview = []
    all_units = all_acc_units(account.unique)
    acc_units = str(account.unit).split(",")

    # Getting all the volume for each unit and the total amount in the account
    for unit in all_units:
        # Table : Total, Transaction In, Transaction Out, Transfer In, Transfer Out, Fee
        table = [0, 0, 0, 0, 0, 0]

        # Transfer In
        for transfer in transfers.all().filter(destination__exact=account, unit__exact=unit):
            table[0] = table[0] + transfer.amount
            table[3] = table[3] + transfer.amount
        # Transfer Out
        for transfer in transfers.all().filter(source__exact=account, unit__exact=unit):
            table[0] = table[0] - transfer.amount
            table[4] = table[4] + transfer.amount
        # Transactions In
        for transaction in transactions.all().filter(input__exact=unit):
            table[0] = table[0] - transaction.amount_in
            table[1] = table[1] + transaction.amount_in
        # Transactions Out
        for transaction in transactions.all().filter(output__exact=unit):
            table[0] = table[0] + transaction.amount_out
            table[2] = table[2] + transaction.amount_out
        # Transfer Fee
        for transfer in transfers.all().filter(source__exact=account, fee_unit__exact=unit):
            table[0] = table[0] - transfer.fee
            table[5] = table[5] + transfer.fee
        # Transaction Fee
        for transaction in transactions.all().filter(fee_unit__exact=unit):
            table[0] = table[0] - transaction.fee
            table[5] = table[5] + transaction.fee
        # Saving results
        table = [unit] + [float_limiter(float(t), 0) for t in table] + [1 if unit in acc_units else 0]
        volume_overview.append(table)

    # Sorting the results
    volume_overview.sort(key=lambda x: x[0])  # Alphabetical order
    volume_overview.sort(key=lambda x: 0 if x[1] != 0 else 1)  # Total Amount=0 at the end
    volume_overview.sort(key=lambda x: 0 if x[0] in acc_units else 1)  # Account units first
    return volume_overview


def pairs_calculations(account: Account, transactions: Transaction):
    """Pairs Calculations

    Args:
        account (Account): The account from which originate transactions
        transactions (Transaction): The transactions to use in the calculations

    Returns:
        list: A list of data for each account pair:
        [the_pair: str, performance_%: float, profit_loss: float, avg_buy_price: float, avg_sell_price: float, tt_fee: float]
    """
    # ---- Pairs Calculations ----
    pairs_summ, pairs_overview = [], []
    acc_units = str(account.unit).split(",")

    # Getting the totals amounts and fees
    for transaction in transactions.all().order_by('date'):
        table, index, pair = None, None, None

        # Pair already saved
        for saved_pair in pairs_summ:
            if f"{transaction.input}/{transaction.output}" == saved_pair[0]:
                table = saved_pair
                index = pairs_summ.index(saved_pair)
                break
            elif f"{transaction.output}/{transaction.input}" == saved_pair[0]:
                table = saved_pair
                index = pairs_summ.index(saved_pair)
                break

        # New pair
        if table is None:
            # The account unit is on the right (better sort by name & calculations)
            pair = f"{transaction.output}/{transaction.input}"
            if transaction.output in acc_units:
                pair = f"{transaction.input}/{transaction.output}"
                if transaction.input in acc_units:
                    if acc_units.index(transaction.input) < acc_units.index(transaction.output):
                        pair = f"{transaction.output}/{transaction.input}"

            # Pair ([1]/[2]), [1]Amount In, [2]Amount Out, [2]Amount In, [1]Amount Out, [1]Fees, [2]Fees
            table = [pair, 0, 0, 0, 0, 0, 0]

        # Filling the table
        if transaction.input == table[0].split("/")[0]:
            table[1] = table[1] + float(transaction.amount_in)
            table[2] = table[2] + float(transaction.amount_out)
        else:
            table[3] = table[3] + float(transaction.amount_in)
            table[4] = table[4] + float(transaction.amount_out)

        if transaction.fee_unit == table[0].split("/")[0]:
            table[5] = table[5] + float(transaction.fee)
        elif transaction.fee_unit == table[0].split("/")[1]:
            table[6] = table[6] + float(transaction.fee)

        # Saving the results
        if index is not None:
            pairs_summ[index] = table
        else:
            pairs_summ.append(table)

    # Calculating the numbers
    for pair in pairs_summ:
        # Account unit on the right, so the left element is the one we 'buy' and 'sell'
        try:
            avg_buy = float_limiter(pair[3] / pair[4], 0)
        except ZeroDivisionError:
            avg_buy = 0
        try:
            avg_sell = float_limiter(pair[2] / pair[1], 0)
        except ZeroDivisionError:
            avg_sell = 0
        pnl = float_limiter(pair[2] - pair[3], 0)
        try:
            perf = round(((pair[2] / pair[3]) - 1) * 100, 2)
        except ZeroDivisionError:
            perf = 0
        fee = float_limiter(pair[6], 0)

        pairs_overview.append([pair[0], perf, pnl, avg_buy, avg_sell, fee])

    # Sorting the results
    pairs_overview.sort(key=lambda x: x[0])
    return pairs_overview
