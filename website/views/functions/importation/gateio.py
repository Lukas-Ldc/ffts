import csv, io
from datetime import datetime
import logging
from website.models import Transaction, Transfer, Standard, Account

def gateio_importer(file, table, trType, acType, acc):

    if file.name.endswith('.csv'):

        if table == "Transactions":
            for column in csv.reader(io.StringIO(file.read().decode('UTF-16')), delimiter='\t'):
                    Transaction.objects.create(
                        account = Account.objects.all().get(unique__exact=acc),
                        market = "",
                        type = typeChecker(trType),
                        date = column[1],
                        input = column[3].split('/')[1] if column[2] == "Buy" else column[3].split('/')[0],
                        output = column[3].split('/')[0] if column[2] == "Buy" else column[3].split('/')[1],
                        amountIn = column[6] if column[2] == "Buy" else column[5],
                        amountOut = column[5] if column[2] == "Buy" else column[6],
                        price = column[4],
                        fee = column[7].split(" ")[0],
                        feeUnit = column[7].split(" ")[1],
                        comment = "",
                    )

        elif table == "CryptoDeposit":
            for column in csv.reader(io.StringIO(file.read().decode('UTF-16')), delimiter='\t'):
                Transfer.objects.create(
                    source = Account.objects.all().get(unique__exact=column[5]) if acType == "Manual" else Account.objects.all().get(unique__exact=acType),
                    destination = Account.objects.all().get(unique__exact=acc),
                    date = column[2],
                    unit = column[3],
                    amount = column[4],
                    fee = 0,
                    feeUnit = "",
                    comment = "",
                )

    elif file.name.endswith('.html'):

        if table == "Dust":
            for html in file:
                
                for line in str(html).split("<tr"):
                    try:
                        time = line.split('<div>')[1].split("</div>")[0]
                        coin = line.split('<td>')[3].split("</td>")[0]
                        amount = line.split('<td>')[4].split("</td>")[0]
                        gt = line.split('<td>')[5].split("</td>")[0]

                        logging.critical(time)

                        Transaction.objects.create(
                            account = Account.objects.all().get(unique__exact=acc),
                            market = "",
                            type = typeChecker(trType),
                            date = time,
                            input = coin,
                            output = "GT",
                            amountIn = amount,
                            amountOut = gt,
                            price = floatRemover(float(amount)/float(gt)),
                            fee = 0,
                            feeUnit = "",
                            comment = "Dust",
                        )
                    except: pass

def typeChecker(t):
    if Standard.objects.all().filter(type__exact='TransactionType', name__exact=t).exists():
        return t
    else:
        return "#IIT#"

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