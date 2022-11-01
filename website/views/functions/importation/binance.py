import csv, io, re, copy
import website.views.functions.dbinterface as dbi
from website.models import Transaction, Account


def binance_importer(file, table, trType, acType, acc, req):

    if file.name.endswith('.csv'):

        accUnit = Account.objects.all().get(unique__exact=acc).unit

        if table == "Transactions":
            file_temp = copy.deepcopy(file)
            new_transa = False

            for column in csv.reader(io.StringIO(file_temp.read().decode('UTF-8')), delimiter=','):
                try: 
                    if len(str(column[7])) > 0:
                        new_transa = True
                except: pass
                break

            if new_transa:
                for column in csv.reader(io.StringIO(file.read().decode('UTF-8')), delimiter=','):
                    dbi.addTransaction(
                        req,
                        True,
                        acc,
                        "",
                        trType,
                        column[0],
                        unitGaverV2(column[1], column[2], column[7], accUnit)[0],
                        unitGaverV2(column[1], column[2], column[7], accUnit)[1],
                        floatGaver(column[5]) if column[2] == "BUY" else floatGaver(column[4]),
                        floatGaver( column[4]) if column[2] == "BUY" else floatGaver(column[5]),
                        floatGaver(column[3]),
                        floatGaver(column[6]),
                        column[7],
                        ""
                    )

            else:
                for column in csv.reader(io.StringIO(file.read().decode('UTF-8')), delimiter=','):
                    dbi.addTransaction(
                        req,
                        True,
                        acc,
                        "",
                        trType,
                        column[0],
                        unitGaver(column[5]) if column[2] == "BUY" else unitGaver(column[4]),
                        unitGaver(column[4]) if column[2] == "BUY" else unitGaver(column[5]),
                        floatGaver(column[5]) if column[2] == "BUY" else floatGaver(column[4]),
                        floatGaver( column[4]) if column[2] == "BUY" else floatGaver(column[5]),
                        floatGaver(column[3]),
                        floatGaver(column[6]),
                        unitGaver(column[6]),
                        ""
                    )

        elif table == "CryptoDeposit" or table == "CryptoWithdrawal":
            for column in csv.reader(io.StringIO(file.read().decode('UTF-8')), delimiter=','):
                dbi.addTransfer(
                    req,
                    True,
                    accGaver(table, "s", acType, column[5], acc),
                    accGaver(table, "d", acType, column[5], acc),
                    column[0],
                    column[1],
                    floatGaver(column[3]),
                    floatGaver(column[4]),
                    column[1],
                    "Via " + column[2]
                )
        
        elif table == "FiatDeposit" or table == "FiatWithdrawal":
            for column in csv.reader(io.StringIO(file.read().decode('UTF-8')), delimiter=','):
                if column[3] == "Successful":
                    dbi.addTransfer(
                        req,
                        True,
                        accGaver(table, "s", acType, "", acc),
                        accGaver(table, "d", acType, "", acc),
                        column[0],
                        column[1],
                        floatGaver(column[2]),
                        floatGaver(column[6]),
                        column[1],
                        column[4]
                    )
        
        elif table == "Other" or table == "OtherBnb":
            file_base = copy.deepcopy(file)
            for column in csv.reader(io.StringIO(file.read().decode('UTF-8')), delimiter=','):

                if column[3] == "Distribution" or column[3] == "Simple Earn Flexible Interest" or column[3] == "Savings Interest":
                    if not (len(column[4]) > 3 and str(column[4]).startswith('LD')):
                        dbi.addTransaction(
                            req,
                            True,
                            acc,
                            "",
                            trType,
                            column[1],
                            str(accUnit).split(",")[0],
                            column[4],
                            0,
                            column[5],
                            0,
                            0,
                            0,
                            column[3] if column[3] == "Distribution" else "Flexible Interest"
                        )

                elif column[3] == "Small assets exchange BNB" and table == "OtherBnb":
                    dbi.addTransaction(
                        req,
                        True,
                        acc,
                        "",
                        trType,
                        column[1],
                        "#DUST#" if column[4] == "BNB" else column[4],
                        "BNB",
                        0 if column[4] == "BNB" else noNegFloat(column[5]),
                        noNegFloat(column[5]) if column[4] == "BNB" else 0,
                        0,
                        0,
                        0,
                        "SAE BNB"
                    )

                elif column[3] == "Simple Earn Locked Subscription" or column[3] == "POS savings purchase":

                    filte_temp = copy.deepcopy(file_base)
                    purchase_found = False
                    pos_interest = []
                    pos_purchase = 0
                    for c in csv.reader(io.StringIO(filte_temp.read().decode('UTF-8')), delimiter=','):

                        if c[4] == column[4] and purchase_found and (c[3] == "Simple Earn Locked Rewards" or c[3] == "POS savings interest"):
                            temp = []
                            for cc in [c[1], c[5]]:
                                temp.append(cc)
                            pos_interest.append(temp)
                            
                        elif c[1] == column[1] and c[4] == column[4] and (c[3] == "Simple Earn Locked Subscription" or c[3] == "POS savings purchase"):
                            purchase_found = True
                            pos_purchase = c[5]

                        elif c[4] == column[4] and purchase_found and (c[3] == "Simple Earn Locked Redemption" or c[3] == "POS savings redemption"):
                            purchase_found = False
                            if str(pos_purchase).replace("-","") == str(c[5]).replace("-",""):
                                for i in pos_interest:
                                    if Transaction.objects.all().filter(account__exact=Account.objects.all().get(unique__exact=acc),date__exact=i[0],output__exact=c[4],amountOut__exact=noNegFloat(i[1])).count() == 0:
                                        dbi.addTransaction(
                                            req,
                                            True,
                                            acc,
                                            "",
                                            trType,
                                            i[0],
                                            str(accUnit).split(",")[0],
                                            c[4],
                                            0,
                                            noNegFloat(i[1]),
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

                        dbi.addTransaction(
                            req,
                            True,
                            acc,
                            "",
                            trType,
                            time,
                            coin,
                            "BNB",
                            amount,
                            bnb,
                            floatRemover(float(amount)/float(bnb)),
                            fee,
                            "BNB",
                            "SAE BNB"
                        )
                    except: pass


def floatGaver(f):
    if f is None or f == "":
        return 0
    else:
        return float(re.sub(r'[A-Za-z,]', '', f))


def noNegFloat(f):
    if f is None or f == "":
        return 0
    else:
        if str(f).startswith("-"):
            return "{:.14f}".format(float(float(str(f)[1:])))
        else:
            return "{:.14f}".format(float(float(f)))

def floatRemover(f):
    if f > 1000:
        return round(f, 2)
    elif f > 100:
        return round(f, 4)
    elif f > 10:
        return round(f, 6)
    elif f > 1:
        return round(f, 8)
    else:
        return round(f, 10)

#Removee numbers: 1.23456700001INCH -> INCH
def unitGaver(f):
    if f is None or f == "":
        return "?"
    else:
        return re.sub(r'[0-9.,]', '', f)


def unitGaverV2(pair, way, feeU, accU):
    unit1 = "##N/A##"

    for u in str(accU + "," + feeU).split(","):
        if str(pair).startswith(u):
            unit1 = u
            break
        elif str(pair).endswith(u):
            unit1 = u
            break
    
    if unit1 != "##N/A##":
        unit2 = str(pair).replace(unit1, "")
        if way == "BUY" and str(pair).startswith(unit1) or way == "SELL" and str(pair).startswith(unit2):
            return [unit2,unit1]
        elif way == "BUY" and str(pair).startswith(unit2) or way == "SELL" and str(pair).startswith(unit1):
            return [unit1,unit2]
    else:
        return [pair,pair]


def accGaver(table, direction, accLinked, manualVal, account):
    if str(table).endswith("Deposit") and direction == "s":
        if accLinked == "Manual":
            return Account.objects.all().get(unique__exact=manualVal).unique
        else:
            return Account.objects.all().get(unique__exact=accLinked).unique
    elif str(table).endswith("Deposit") and direction == "d":
        return Account.objects.all().get(unique__exact=account).unique
    elif str(table).endswith("Withdrawal") and direction == "d":
        if accLinked == "Manual":
            return Account.objects.all().get(unique__exact=manualVal).unique
        else:
            return Account.objects.all().get(unique__exact=accLinked).unique
    elif str(table).endswith("Withdrawal") and direction == "s":
        return Account.objects.all().get(unique__exact=account).unique
