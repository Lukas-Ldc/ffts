import csv, io
from website.models import Transaction, Transfer, Standard, Account


def ib_importer(file, trType, acType, acc):

    if file.name.endswith('.csv'):

        forex_fee = str(Account.objects.all().get(unique__exact=acc).unit).split(",")[0]

        for column in csv.reader(io.StringIO(file.read().decode('UTF-8')), delimiter=','):

            if column[0] == "Trades" and column[1] == "Data" and column[2] == "Order" and column[3] == "Forex":
                Transaction.objects.create(
                    account = Account.objects.all().get(unique__exact=acc),
                    market = "",
                    type = typeChecker(trType),
                    date = str(column[6]).replace(",", ""),
                    input = str(column[5]).split(".")[1] if floatGaver(column[7],True) > 0 else str(column[5]).split(".")[0],
                    output = str(column[5]).split(".")[0] if floatGaver(column[7],True) > 0 else str(column[5]).split(".")[1],
                    amountIn = floatGaver(column[10],False) if floatGaver(column[7],True) > 0 else floatGaver(column[7],False),
                    amountOut = floatGaver(column[7],False) if floatGaver(column[7],True) > 0 else floatGaver(column[10],False),
                    price = floatGaver(column[8],False),
                    fee = floatGaver(column[11],False),
                    feeType = "+" + forex_fee,
                    comment = column[3],
                )

            elif column[0] == "Trades" and column[1] == "Data" and column[2] == "Order":
                Transaction.objects.create(
                    account = Account.objects.all().get(unique__exact=acc),
                    market = "",
                    type = typeChecker(trType),
                    date = str(column[6]).replace(",", ""),
                    input = column[4] if floatGaver(column[7],True) > 0 else column[5],
                    output = column[5] if floatGaver(column[7],True) > 0 else column[4],
                    amountIn = floatGaver(column[10],False) if floatGaver(column[7],True) > 0 else floatGaver(column[7],False),
                    amountOut = floatGaver(column[7],False) if floatGaver(column[7],True) > 0 else floatGaver(column[10],False),
                    price = floatGaver(column[8],False),
                    fee = floatGaver(column[11],False),
                    feeType = "+" + column[4] if len(column[4]) > 0 else "",
                    comment = column[3],
                )

            elif column[0] == "Deposits & Withdrawals" and column[1] == "Data" and column[2] != "Total":
                Transfer.objects.create(
                        source = Account.objects.all().get(unique__exact=acType) if floatGaver(column[5],True) > 0 else Account.objects.all().get(unique__exact=acc),
                        destination = Account.objects.all().get(unique__exact=acc) if floatGaver(column[5],True) > 0 else Account.objects.all().get(unique__exact=acType),
                        date = column[3],
                        unit = column[2],
                        amount = floatGaver(column[5],False),
                        fee = 0,
                        feeType = "",
                        comment = column[4],
                    )

            elif column[0] == "Transaction Fees" and column[1] == "Data" and column[2] != "Total":
                Transaction.objects.create(
                    account = Account.objects.all().get(unique__exact=acc),
                    market = "",
                    type = typeChecker(trType),
                    date = column[4],
                    input = column[3],
                    output = column[5],
                    amountIn = 0,
                    amountOut = 0,
                    price = 0,
                    fee = floatGaver(column[9],False),
                    feeType = "+" + column[3] if len(column[3]) > 0 else "",
                    comment = column[6],
                )

            elif column[0] == "Account Information" and column[1] == "Data" and column[2] == "Base Currency":
                forex_fee = column[3]

            elif column[0] == "Trades" and column[1] == "Header":
                if str(column[11])[:8] == "Comm in ":
                    forex_fee = str(column[11])[8:]


def floatGaver(f,n):
    if f is None or f == "":
        return 0
    else:
        if n:
            return round(float(f.replace(",",".")), 4)
        else:
            return round(float(f.replace(",",".").replace("-","")), 4)

def typeChecker(t):
    if Standard.objects.all().filter(type__exact='TransactionType', name__exact=t).exists():
        return t
    else:
        return "#IIT#"