from io import StringIO
from copy import deepcopy
from re import sub as resub
from csv import reader as csvreader
from website.models import Account
from website.views.functions.dbinterface import add_transaction, add_transfer


def binance_importer(file, table: str, tr_type: str, transf_acc: str, acc: str, request):
    """Import a binance export

    Args:
        file (file): The file that contains the data to import
        table (str): The type of data imported
        tr_type (str): The type of transaction
        transf_acc (str): The account linked to the withdrawals & deposits
        acc (str): The account that will receive the imported data
        request (HttpRequest): The request made to send the file
    """

    if file.name.endswith('.csv'):

        # Unit of the account
        # FIXME: Multi units account will not work
        acc_unit = Account.objects.all().get(unique__exact=acc).unit

        # The user wants to import transactions
        if table == "Transactions":
            file_temp = deepcopy(file)
            new_transa = False

            # TODO: Remove old transaction importer (and deepcopy)
            for column in csvreader(StringIO(file_temp.read().decode('UTF-8')), delimiter=','):
                try:
                    if len(str(column[7])) > 0:
                        new_transa = True
                except IndexError:
                    pass
                break

            if new_transa:
                for column in csvreader(StringIO(file.read().decode('UTF-8')), delimiter=','):
                    add_transaction(
                        request,
                        True,
                        acc,
                        "",
                        tr_type,
                        column[0],
                        unit_gaver_v2(column[1], column[2], column[7], acc_unit)[0],
                        unit_gaver_v2(column[1], column[2], column[7], acc_unit)[1],
                        float_gaver(column[5]) if column[2] == "BUY" else float_gaver(column[4]),
                        float_gaver(column[4]) if column[2] == "BUY" else float_gaver(column[5]),
                        float_gaver(column[3]),
                        float_gaver(column[6]),
                        column[7],
                        ""
                    )

            else:
                for column in csvreader(StringIO(file.read().decode('UTF-8')), delimiter=','):
                    add_transaction(
                        request,
                        True,
                        acc,
                        "",
                        tr_type,
                        column[0],
                        unit_gaver(column[5]) if column[2] == "BUY" else unit_gaver(column[4]),
                        unit_gaver(column[4]) if column[2] == "BUY" else unit_gaver(column[5]),
                        float_gaver(column[5]) if column[2] == "BUY" else float_gaver(column[4]),
                        float_gaver(column[4]) if column[2] == "BUY" else float_gaver(column[5]),
                        float_gaver(column[3]),
                        float_gaver(column[6]),
                        unit_gaver(column[6]),
                        ""
                    )

        # The user wants to import crypto deposits or withdrawals
        elif table == "CryptoDeposit" or table == "CryptoWithdrawal":
            for column in csvreader(StringIO(file.read().decode('UTF-8')), delimiter=','):
                add_transfer(
                    request,
                    True,
                    acc_gaver(table, "s", transf_acc, column[5], acc),
                    acc_gaver(table, "d", transf_acc, column[5], acc),
                    column[0],
                    column[1],
                    float_gaver(column[3]),
                    float_gaver(column[4]),
                    column[1],
                    "Via " + column[2]
                )

        # The user wants to import fiat deposits or withdrawals
        elif table == "FiatDeposit" or table == "FiatWithdrawal":
            for column in csvreader(StringIO(file.read().decode('UTF-8')), delimiter=','):
                if column[3] == "Successful":
                    add_transfer(
                        request,
                        True,
                        acc_gaver(table, "s", transf_acc, "", acc),
                        acc_gaver(table, "d", transf_acc, "", acc),
                        column[0],
                        column[1],
                        float_gaver(column[2]),
                        float_gaver(column[6]),
                        column[1],
                        column[4]
                    )

        # The user wants to import interests & dust
        elif table == "Other" or table == "OtherBnb":
            file_base = deepcopy(file)  # Making a copy to be able to read in parallel if PoS

            for column in csvreader(StringIO(file.read().decode('UTF-8')), delimiter=','):

                # Simple interest (cancel anytime, what you've earned is earned) or distribution
                if column[3] == "Distribution" or column[3] == "Simple Earn Flexible Interest" or column[3] == "Savings Interest":
                    if not (len(column[4]) > 3 and str(column[4]).startswith('LD')):
                        add_transaction(
                            request,
                            True,
                            acc,
                            "",
                            tr_type,
                            column[1],
                            str(acc_unit).split(",")[0],
                            column[4],
                            0,
                            column[5],
                            0,
                            0,
                            0,
                            column[3] if column[3] == "Distribution" else "Flexible Interest"
                        )

                # Dust (not the best way: output and input separated in 2 transactions)
                elif column[3] == "Small assets exchange BNB" and table == "OtherBnb":
                    add_transaction(
                        request,
                        True,
                        acc,
                        "",
                        tr_type,
                        column[1],
                        "#DUST#" if column[4] == "BNB" else column[4],
                        "BNB",
                        0 if column[4] == "BNB" else no_neg_float(column[5]),
                        no_neg_float(column[5]) if column[4] == "BNB" else 0,
                        0,
                        0,
                        0,
                        "SAE BNB"
                    )

                # Locked interest (if you cancel, you wont earn the past interest)
                # If 2 subscriptions for the same asset overlap + one of them is canceled : wrong numbers saved
                # TODO: remove old naming of col[3] for conditions
                elif column[3] == "Simple Earn Locked Subscription" or column[3] == "POS savings purchase":

                    filte_temp = deepcopy(file_base)  # New copy for each subscription to start the read from the begining # TODO: optimisation possible ?
                    purchase_found = False  # The subscription has been found in the new copy
                    pos_interest = []  # The interest during the subscription
                    pos_purchase = 0  # The amount of the subscription

                    for col in csvreader(StringIO(filte_temp.read().decode('UTF-8')), delimiter=','):

                        # If subscription found and interest from the subscription asset
                        if col[4] == column[4] and purchase_found and (col[3] == "Simple Earn Locked Rewards" or col[3] == "POS savings interest"):
                            temp = []
                            for ccol in [col[1], col[5]]:
                                temp.append(ccol)
                            pos_interest.append(temp)

                        # Trying to find the subscription
                        elif col[1] == column[1] and col[4] == column[4] and (col[3] == "Simple Earn Locked Subscription" or col[3] == "POS savings purchase"):
                            purchase_found = True
                            pos_purchase = col[5]

                        # Redemption has been found
                        elif col[4] == column[4] and purchase_found and (col[3] == "Simple Earn Locked Redemption" or col[3] == "POS savings redemption"):
                            # If not canceled (purchase amount == redemption amount)
                            if str(pos_purchase).replace("-", "") == str(col[5]).replace("-", ""):
                                # Saving transactions (2 subscritpions overlap not a problem: anti-duplicate protection)
                                for i in pos_interest:
                                    add_transaction(
                                        request,
                                        True,
                                        acc,
                                        "",
                                        tr_type,
                                        i[0],
                                        str(acc_unit).split(",")[0],
                                        col[4],
                                        0,
                                        no_neg_float(i[1]),
                                        0,
                                        0,
                                        0,
                                        "Locked Subscription"
                                    )
                            break

    elif file.name.endswith('.html'):

        # The user wants to import dust
        if table == "BnbHtml":

            for html in file:
                # For each dust conversion
                for line in str(html).split("css-1f50q6c"):

                    try:
                        # Extracting the data from the HTML
                        temp_l = line.split("css-vurnku")[0]
                        time = temp_l.split('<div data-type="table-min-row" class="css-1uzrl9p">')[1].split("</div>")[0]
                        coin = temp_l.split('<div data-type="table-min-row" class="css-vjfjtb">')[1].split("</div>")[0]
                        amount = temp_l.split('<div data-type="table-min-row" class="css-vjfjtb">')[2].split("</div>")[0]
                        fee = temp_l.split('<div data-type="table-min-row" class="css-1dm9igw">')[1].split("</div>")[0]
                        bnb = temp_l.split('<div data-type="table-min-row" class="css-1dm9igw">')[2].split("</div>")[0]

                        add_transaction(
                            request,
                            True,
                            acc,
                            "",
                            tr_type,
                            time,
                            coin,
                            "BNB",
                            amount,
                            bnb,
                            float_remover(float(amount) / float(bnb)),
                            fee,
                            "BNB",
                            "SAE BNB"
                        )
                    except IndexError:
                        pass


def float_gaver(number: str):
    """Removes any letter and comma from a string

    Args:
        number (str): The string to clean

    Returns:
        float: The cleaned number
    """
    if number is None or number == "":
        return 0
    else:
        return float(resub(r'[A-Za-z,]', '', number))


def no_neg_float(number: str or int or float):
    """Transforms a negative number in a positive one

    Args:
        number (str or int or float): The element to convert

    Returns:
        float: The non negative float
    """
    if number is None or number == "":
        return 0
    else:
        if str(number).startswith("-"):
            return "{:.14f}".format(float(float(str(number)[1:])))
        else:
            return "{:.14f}".format(float(float(number)))
    # TODO: Optimisation possible ?


def float_remover(number: float):
    """Depending on the size of the number, limits the number of digits after the decimal point

    Args:
        number (float): The number to clean

    Returns:
        float: The cleaned number
    """
    if number > 1000:
        return round(number, 2)
    if number > 100:
        return round(number, 4)
    if number > 10:
        return round(number, 6)
    if number > 1:
        return round(number, 8)
    return round(number, 10)


def unit_gaver(unit: str):
    """# TODO: To be removed"""
    if unit is None or unit == "":
        return "?"
    else:
        return resub(r'[0-9.,]', '', unit)


def unit_gaver_v2(pair: str, way: str, fee_u: str, acc_u: str):
    """Separates a pair (BTCUSDT) into two different tickers (BTC, USDT).
    Using the unit account, the fee unit: else retrun

    Args:
        pair (str): The pair to spli (BTCUSDT)
        way (str): BUY or SELL
        fee_u (str): The unit of the fee
        acc_u (str): The unit of the account

    Returns:
        list: (INPUT, OUTPUT) or (PAIR, PAIR)
    """
    # TODO: Create database unit with all the account's transactions for more accuracy
    unit1 = "##N/A##"

    # Trying to gess the unit according to the account or fee unit
    for unit in [acc_u, fee_u]:
        if str(pair).startswith(unit):
            unit1 = unit
            break
        elif str(pair).endswith(unit):
            unit1 = unit
            break

    # Unit guessed
    if unit1 != "##N/A##":
        unit2 = str(pair).replace(unit1, "")  # Removing unit guessed to get other unit

        if way == "BUY" and str(pair).startswith(unit1) or way == "SELL" and str(pair).startswith(unit2):
            return [unit2, unit1]
        elif way == "BUY" and str(pair).startswith(unit2) or way == "SELL" and str(pair).startswith(unit1):
            return [unit1, unit2]

    # Not guessed
    return [pair, pair]


def acc_gaver(table: str, direction: str, acc_linked: str, manual_val: str, account: str):
    """_summary_

    Args:
        table (str): The table selected for the import (ends with Withdrawal or Deposit)
        direction (str): You need the source account ("s") or the destination ("d")
        acc_linked (str): Manual or the selected account (one set in the HTML form)
        manual_val (str): If Manual use this account (one in the CSV)
        account (str): The account in which the data is imported

    Returns:
        Account: The account needed
    """
    # TODO: combination of acc_linked and manual_val possible ?
    # Source needed for a deposit
    if str(table).endswith("Deposit") and direction == "s":
        if acc_linked == "Manual":
            return Account.objects.all().get(unique__exact=manual_val).unique
        else:
            return Account.objects.all().get(unique__exact=acc_linked).unique

    # Destination needed for a withdrdepositawal
    elif str(table).endswith("Deposit") and direction == "d":
        return Account.objects.all().get(unique__exact=account).unique

    # Destination needed for a withdrawal
    elif str(table).endswith("Withdrawal") and direction == "d":
        if acc_linked == "Manual":
            return Account.objects.all().get(unique__exact=manual_val).unique
        else:
            return Account.objects.all().get(unique__exact=acc_linked).unique

    # Source needed for a withdrawal
    elif str(table).endswith("Withdrawal") and direction == "s":
        return Account.objects.all().get(unique__exact=account).unique
