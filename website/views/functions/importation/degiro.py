import csv, io
from datetime import datetime
from website.models import Transaction, Transfer, Standard, Account


def degiro_importer(file, table, trType, acType, acc):

    if file.name.endswith('.csv'):

        if table == "Transactions":
            for column in csv.reader(io.StringIO(file.read().decode('UTF-8')), delimiter=','):
                Transaction.objects.create(
                    account = Account.objects.all().get(unique__exact=acc),
                    market = column[4],
                    type = typeChecker(trType),
                    date = dateGaver(column[0]) + ' ' + column[1],
                    input = column[10] if float(column[6]) > 0 else column[2],
                    output = column[2] if float(column[6]) > 0 else column[10],
                    amountIn = floatGaver(column[9]) if float(column[6]) > 0 else floatGaver(column[6]),
                    amountOut = floatGaver( column[6]) if float(column[6]) > 0 else floatGaver(column[9]),
                    price = floatGaver(column[7]),
                    fee = floatGaver(column[14]),
                    feeUnit = column[15] if len(column[15]) > 0 else "",
                    comment = "",
                )

        elif table == "Transfers":
            change = False
            for column in csv.reader(io.StringIO(file.read().decode('UTF-8')), delimiter=','):

                if column[5] == "DEPOSIT":
                    Transfer.objects.create(
                        source = Account.objects.all().get(unique__exact=acType),
                        destination = Account.objects.all().get(unique__exact=acc),
                        date = dateGaver(column[0]) + ' ' + column[1],
                        unit = column[7],
                        amount = floatGaver(column[8]),
                        fee = 0,
                        feeUnit = "",
                        comment = "",
                    )

                elif column[5] == "WITHDRAWAL":
                    Transfer.objects.create(
                        source = Account.objects.all().get(unique__exact=acc),
                        destination = Account.objects.all().get(unique__exact=acType),
                        date = dateGaver(column[0]) + ' ' + column[1],
                        unit = column[7],
                        amount = floatGaver(column[8]),
                        fee = 0,
                        feeUnit = "",
                        comment = "",
                    )

                elif column[5] == "CHANGE_IN":
                    if change:
                        last.output = column[7]
                        last.amountOut = floatGaver(column[8])
                        last.save()
                        change = False

                    else:
                        last = Transaction.objects.create(
                            account = Account.objects.all().get(unique__exact=acc),
                            market = "",
                            type = typeChecker(trType),
                            date = dateGaver(column[0]) + ' ' + column[1],
                            input = "TEMP",
                            output = column[7],
                            amountIn = 0,
                            amountOut = floatGaver(column[8]),
                            price = floatGaver(column[6]),
                            fee = 0,
                            feeUnit = "",
                            comment = "",
                        )
                        change = True

                elif column[5] == "CHANGE_OUT":
                    if change:
                        last.input = column[7]
                        last.amountIn = floatGaver(column[8])
                        last.save()
                        change = False
                        
                    else:
                        last = Transaction.objects.create(
                            account = Account.objects.all().get(unique__exact=acc),
                            market = "",
                            type = typeChecker(trType),
                            date = dateGaver(column[0]) + ' ' + column[1],
                            input = column[7],
                            output = "TEMP",
                            amountIn = floatGaver(column[8]),
                            amountOut = 0,
                            price = opp(floatGaver(column[6])),
                            fee = 0,
                            feeUnit = "",
                            comment = "",
                        )
                        change = True

def floatGaver(f):
    if f is None or f == "":
        return 0
    else:
        return float(f.replace(",",".").replace("-",""))

def typeChecker(t):
    if Standard.objects.all().filter(type__exact='TransactionType', name__exact=t).exists():
        return t
    else:
        return "#IIT#"

def dateGaver(d):
    return datetime.strptime(d, '%d-%m-%Y').strftime('%Y-%m-%d')

def opp(n):
    try:
        return round(1 / n, 4)
    except:
        return 0