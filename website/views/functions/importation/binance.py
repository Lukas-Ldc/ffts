import csv, io, re, copy
from website.models import Transaction, Transfer, Standard, Account


def binance_importer(file, table, trType, acType, acc):

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
                    Transaction.objects.create(
                        account = Account.objects.all().get(unique__exact=acc),
                        market = "",
                        type = typeChecker(trType),
                        date = column[0],
                        input = unitGaverV2(column[1], column[2], column[7], accUnit)[0],
                        output = unitGaverV2(column[1], column[2], column[7], accUnit)[1],
                        amountIn = floatGaver(column[5]) if column[2] == "BUY" else floatGaver(column[4]),
                        amountOut = floatGaver( column[4]) if column[2] == "BUY" else floatGaver(column[5]),
                        price = floatGaver(column[3]),
                        fee = floatGaver(column[6]),
                        feeUnit = column[7],
                        comment = "",
                    )

            else:
                for column in csv.reader(io.StringIO(file.read().decode('UTF-8')), delimiter=','):
                    Transaction.objects.create(
                        account = Account.objects.all().get(unique__exact=acc),
                        market = "",
                        type = typeChecker(trType),
                        date = column[0],
                        input = unitGaver(column[5]) if column[2] == "BUY" else unitGaver(column[4]),
                        output = unitGaver(column[4]) if column[2] == "BUY" else unitGaver(column[5]),
                        amountIn = floatGaver(column[5]) if column[2] == "BUY" else floatGaver(column[4]),
                        amountOut = floatGaver( column[4]) if column[2] == "BUY" else floatGaver(column[5]),
                        price = floatGaver(column[3]),
                        fee = floatGaver(column[6]),
                        feeUnit = unitGaver(column[6]),
                        comment = "",
                    )

        elif table == "CryptoDeposit" or table == "CryptoWithdrawal":
            for column in csv.reader(io.StringIO(file.read().decode('UTF-8')), delimiter=','):
                Transfer.objects.create(
                    source = accGaver(table, "s", acType, column[5], acc),
                    destination = accGaver(table, "d", acType, column[5], acc),
                    date = column[0],
                    unit = column[1],
                    amount = floatGaver(column[3]),
                    fee = floatGaver(column[4]),
                    feeUnit = column[1],
                    comment = "Via " + column[2],
                )
        
        elif table == "FiatDeposit" or table == "FiatWithdrawal":
            for column in csv.reader(io.StringIO(file.read().decode('UTF-8')), delimiter=','):
                if column[3] == "Successful":
                    Transfer.objects.create(
                        source = accGaver(table, "s", acType, "", acc),
                        destination = accGaver(table, "d", acType, "", acc),
                        date = column[0],
                        unit = column[1],
                        amount = floatGaver(column[2]),
                        fee = floatGaver(column[6]),
                        feeUnit = column[1],
                        comment = column[4],
                    )
        
        elif table == "Other":
            file_base = copy.deepcopy(file)
            for column in csv.reader(io.StringIO(file.read().decode('UTF-8')), delimiter=','):

                if column[3] == "Distribution" or column[3] == "Savings Interest":
                    if not (len(column[4]) > 3 and str(column[4]).startswith('LD')):
                        Transaction.objects.create(
                            account = Account.objects.all().get(unique__exact=acc),
                            market = "",
                            type = typeChecker(trType),
                            date = column[1],
                            input = str(accUnit).split(",")[0],
                            output = column[4],
                            amountIn = 0,
                            amountOut = float(column[5]),
                            price = 0,
                            fee = 0,
                            feeUnit = 0,
                            comment = column[3],
                        )

                elif column[3] == "Small assets exchange BNB":
                    Transaction.objects.create(
                            account = Account.objects.all().get(unique__exact=acc),
                            market = "",
                            type = typeChecker(trType),
                            date = column[1],
                            input = "#DUST#" if column[4] == "BNB" else column[4],
                            output = "BNB" if column[4] == "BNB" else "BNB",
                            amountIn = 0 if column[4] == "BNB" else noNegFloat(column[5]),
                            amountOut = noNegFloat(column[5]) if column[4] == "BNB" else 0,
                            price = 0,
                            fee = 0,
                            feeUnit = 0,
                            comment = "Small Assets Exchange",
                        )

                elif column[3] == "POS savings purchase":

                    filte_temp = copy.deepcopy(file_base)
                    purchase_found = False
                    pos_interest = []
                    pos_purchase = 0
                    for c in csv.reader(io.StringIO(filte_temp.read().decode('UTF-8')), delimiter=','):

                        if c[3] == "POS savings interest" and c[4] == column[4] and purchase_found:
                            temp = []
                            for cc in [c[1], c[5]]:
                                temp.append(cc)
                            pos_interest.append(temp)
                            
                        elif c[1] == column[1] and c[3] == "POS savings purchase" and c[4] == column[4]:
                            purchase_found = True
                            pos_purchase = c[5]

                        elif c[3] == "POS savings redemption" and c[4] == column[4] and purchase_found:
                            purchase_found = False
                            if str(pos_purchase).replace("-","") == str(c[5]).replace("-",""):
                                for i in pos_interest:
                                    Transaction.objects.create(
                                        account = Account.objects.all().get(unique__exact=acc),
                                        market = "",
                                        type = typeChecker(trType),
                                        date = i[0],
                                        input = str(accUnit).split(",")[0],
                                        output = c[4],
                                        amountIn = 0,
                                        amountOut = noNegFloat(i[1]),
                                        price = 0,
                                        fee = 0,
                                        feeUnit = 0,
                                        comment = "POS Interest",
                                    )
                            break


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
            return float(str(f)[1:])
        else:
            return float(f)


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


def typeChecker(t):
    if Standard.objects.all().filter(type__exact='TransactionType', name__exact=t).exists():
        return t
    else:
        return "#IIT#"


def accGaver(table, direction, accLinked, manualVal, account):
    if str(table).endswith("Deposit") and direction == "s":
        if accLinked == "Manual":
            return Account.objects.all().get(unique__exact=manualVal)
        else:
            return Account.objects.all().get(unique__exact=accLinked)
    elif str(table).endswith("Deposit") and direction == "d":
        return Account.objects.all().get(unique__exact=account)
    elif str(table).endswith("Withdrawal") and direction == "d":
        if accLinked == "Manual":
            return Account.objects.all().get(unique__exact=manualVal)
        else:
            return Account.objects.all().get(unique__exact=accLinked)
    elif str(table).endswith("Withdrawal") and direction == "s":
        return Account.objects.all().get(unique__exact=account)
