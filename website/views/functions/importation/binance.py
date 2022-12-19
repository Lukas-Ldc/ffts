from io import StringIO
from copy import deepcopy
from re import sub as resub
from csv import reader as csvreader
from website.models import Transaction, Account
from website.views.functions.dbinterface import add_transaction, add_transfer


def binance_importer(file, table, tr_type, ac_type, acc, req):

    if file.name.endswith('.csv'):

        acc_unit = Account.objects.all().get(unique__exact=acc).unit

        if table == "Transactions":
            file_temp = deepcopy(file)
            new_transa = False

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
                        req,
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
                        req,
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

        elif table == "CryptoDeposit" or table == "CryptoWithdrawal":
            for column in csvreader(StringIO(file.read().decode('UTF-8')), delimiter=','):
                add_transfer(
                    req,
                    True,
                    acc_gaver(table, "s", ac_type, column[5], acc),
                    acc_gaver(table, "d", ac_type, column[5], acc),
                    column[0],
                    column[1],
                    float_gaver(column[3]),
                    float_gaver(column[4]),
                    column[1],
                    "Via " + column[2]
                )

        elif table == "FiatDeposit" or table == "FiatWithdrawal":
            for column in csvreader(StringIO(file.read().decode('UTF-8')), delimiter=','):
                if column[3] == "Successful":
                    add_transfer(
                        req,
                        True,
                        acc_gaver(table, "s", ac_type, "", acc),
                        acc_gaver(table, "d", ac_type, "", acc),
                        column[0],
                        column[1],
                        float_gaver(column[2]),
                        float_gaver(column[6]),
                        column[1],
                        column[4]
                    )

        elif table == "Other" or table == "OtherBnb":
            file_base = deepcopy(file)
            for column in csvreader(StringIO(file.read().decode('UTF-8')), delimiter=','):

                if column[3] == "Distribution" or column[3] == "Simple Earn Flexible Interest" or column[3] == "Savings Interest":
                    if not (len(column[4]) > 3 and str(column[4]).startswith('LD')):
                        add_transaction(
                            req,
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

                elif column[3] == "Small assets exchange BNB" and table == "OtherBnb":
                    add_transaction(
                        req,
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

                elif column[3] == "Simple Earn Locked Subscription" or column[3] == "POS savings purchase":

                    filte_temp = deepcopy(file_base)
                    purchase_found = False
                    pos_interest = []
                    pos_purchase = 0
                    for col in csvreader(StringIO(filte_temp.read().decode('UTF-8')), delimiter=','):

                        if col[4] == column[4] and purchase_found and (col[3] == "Simple Earn Locked Rewards" or col[3] == "POS savings interest"):
                            temp = []
                            for ccol in [col[1], col[5]]:
                                temp.append(ccol)
                            pos_interest.append(temp)

                        elif col[1] == column[1] and col[4] == column[4] and (col[3] == "Simple Earn Locked Subscription" or col[3] == "POS savings purchase"):
                            purchase_found = True
                            pos_purchase = col[5]

                        elif col[4] == column[4] and purchase_found and (col[3] == "Simple Earn Locked Redemption" or col[3] == "POS savings redemption"):
                            purchase_found = False
                            if str(pos_purchase).replace("-", "") == str(col[5]).replace("-", ""):
                                for i in pos_interest:
                                    if Transaction.objects.all().filter(
                                        account__exact=Account.objects.all().get(unique__exact=acc),
                                        date__exact=i[0], output__exact=col[4],
                                        amountOut__exact=no_neg_float(i[1])
                                    ).count() == 0:
                                        add_transaction(
                                            req,
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

        if table == "BnbHtml":

            for html in file:

                for line in str(html).split("css-1f50q6c"):

                    try:
                        temp_l = line.split("css-vurnku")[0]
                        time = temp_l.split('<div data-type="table-min-row" class="css-1uzrl9p">')[1].split("</div>")[0]
                        coin = temp_l.split('<div data-type="table-min-row" class="css-vjfjtb">')[1].split("</div>")[0]
                        amount = temp_l.split('<div data-type="table-min-row" class="css-vjfjtb">')[2].split("</div>")[0]
                        fee = temp_l.split('<div data-type="table-min-row" class="css-1dm9igw">')[1].split("</div>")[0]
                        bnb = temp_l.split('<div data-type="table-min-row" class="css-1dm9igw">')[2].split("</div>")[0]

                        add_transaction(
                            req,
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


def float_gaver(number):
    if number is None or number == "":
        return 0
    else:
        return float(resub(r'[A-Za-z,]', '', number))


def no_neg_float(number):
    if number is None or number == "":
        return 0
    else:
        if str(number).startswith("-"):
            return "{:.14f}".format(float(float(str(number)[1:])))
        else:
            return "{:.14f}".format(float(float(number)))


def float_remover(number):
    if number > 1000:
        return round(number, 2)
    elif number > 100:
        return round(number, 4)
    elif number > 10:
        return round(number, 6)
    elif number > 1:
        return round(number, 8)
    else:
        return round(number, 10)


def unit_gaver(number):

    if number is None or number == "":
        return "?"
    else:
        return resub(r'[0-9.,]', '', number)


def unit_gaver_v2(pair, way, fee_u, acc_u):
    unit1 = "##N/A##"

    for unit in str(acc_u + "," + fee_u).split(","):
        if str(pair).startswith(unit):
            unit1 = unit
            break
        elif str(pair).endswith(unit):
            unit1 = unit
            break

    if unit1 != "##N/A##":
        unit2 = str(pair).replace(unit1, "")
        if way == "BUY" and str(pair).startswith(unit1) or way == "SELL" and str(pair).startswith(unit2):
            return [unit2, unit1]
        elif way == "BUY" and str(pair).startswith(unit2) or way == "SELL" and str(pair).startswith(unit1):
            return [unit1, unit2]
    else:
        return [pair, pair]


def acc_gaver(table, direction, acc_linked, manual_val, account):
    if str(table).endswith("Deposit") and direction == "s":
        if acc_linked == "Manual":
            return Account.objects.all().get(unique__exact=manual_val).unique
        else:
            return Account.objects.all().get(unique__exact=acc_linked).unique
    elif str(table).endswith("Deposit") and direction == "d":
        return Account.objects.all().get(unique__exact=account).unique
    elif str(table).endswith("Withdrawal") and direction == "d":
        if acc_linked == "Manual":
            return Account.objects.all().get(unique__exact=manual_val).unique
        else:
            return Account.objects.all().get(unique__exact=acc_linked).unique
    elif str(table).endswith("Withdrawal") and direction == "s":
        return Account.objects.all().get(unique__exact=account).unique
