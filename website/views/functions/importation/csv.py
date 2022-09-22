import csv, io
from website.models import Transaction, Transfer, Account, Standard

def csv_importer(file, table, un):

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
                    feeUnit = column[10],
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
                    feeUnit = column[6],
                    comment = column[7],
                )

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
