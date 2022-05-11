import csv, io
from website.models import Transaction, Transfer, Account, Standard

def csv_importer(file, table, fu, fc, un):

    if file.name.endswith('.csv'):

        if table == "Transactions":
            for column in csv.reader(io.StringIO(file.read().decode('UTF-8')), delimiter=','):
                Transaction.objects.create(
                    account = Account.objects.all().get(unique__exact=column[0]),
                    market = column[1],
                    type = typeChecker(column[2]),
                    date = column[3],
                    input = column[4],
                    output = column[5],
                    amountIn = floatGaver(column[6]),
                    amountOut = floatGaver(column[7]),
                    price = floatGaver(column[8]),
                    fee = floatGaver(column[9]),
                    feeType = feeTypeGuesser(fu, fc, column[4], column[5], un, column[10]),
                    comment = column[11],
                )

        elif table == "Transfers":
            for column in csv.reader(io.StringIO(file.read().decode('UTF-8')), delimiter=','):
                Transfer.objects.create(
                    source = Account.objects.all().get(unique__exact=column[0]),
                    destination = Account.objects.all().get(unique__exact=column[1]),
                    date = column[2],
                    unit = column[3],
                    amount = floatGaver(column[4]),
                    fee = floatGaver(column[5]),
                    feeType = feeTypeGuesser(fu, fc, column[4], column[4], un, column[6]),
                    comment = column[7],
                )

def feeTypeGuesser(fu, fc, amI, amO, un, ft):
    if len(ft) < 1:
        if fc == "Inside":
            ft = "-"
        elif fc == "Outside":
            ft = "+"
        if fu == "Input":
            ft = ft + amI
        elif fu == "Output":
            ft = ft + amO
        elif fu == "Account":
            ft = ft + un
    return ft

def floatGaver(f):
    if f is None or f == "":
        return 0
    else:
        return float(f.replace(",","."))

def typeChecker(t):
    if Standard.objects.all().filter(type__exact='TransactionType', name__exact=t).exists():
        return t
    else:
        return "#IIT#"
