import csv, io
import website.views.functions.dbinterface as dbi
from website.models import Account


def ib_importer(file, trType, acTypeBa, acTypeIa, acc, req):

    if file.name.endswith('.csv'):

        forex_fee = str(Account.objects.all().get(unique__exact=acc).unit).split(",")[0]

        for column in csv.reader(io.StringIO(file.read().decode('UTF-8')), delimiter=','):

            if column[0] == "Trades" and column[1] == "Data" and column[2] == "Order" and column[3] == "Forex":
                dbi.addTransaction(
                    req,
                    True,
                    acc,
                    "",
                    trType,
                    str(column[6]).replace(",", ""),
                    str(column[5]).split(".")[1] if floatGaver(column[7]) > 0 else str(column[5]).split(".")[0],
                    str(column[5]).split(".")[0] if floatGaver(column[7]) > 0 else str(column[5]).split(".")[1],
                    floatGaver(column[10]) if floatGaver(column[7]) > 0 else floatGaver(column[7]),
                    floatGaver(column[7]) if floatGaver(column[7]) > 0 else floatGaver(column[10]),
                    floatGaver(column[8]),
                    floatGaver(column[11]),
                    forex_fee,
                    column[3]
                )

            elif column[0] == "Trades" and column[1] == "Data" and column[2] == "Order":
                dbi.addTransaction(
                    req,
                    True,
                    acc,
                    "",
                    trType,
                    str(column[6]).replace(",", ""),
                    column[4] if floatGaver(column[7]) > 0 else column[5],
                    column[5] if floatGaver(column[7]) > 0 else column[4],
                    floatGaver(column[10]) if floatGaver(column[7]) > 0 else floatGaver(column[7]),
                    floatGaver(column[7]) if floatGaver(column[7]) > 0 else floatGaver(column[10]),
                    floatGaver(column[8]),
                    floatGaver(column[11]),
                    column[4] if len(column[4]) > 0 else "",
                    column[3]
                )

            elif column[0] == "Deposits & Withdrawals" and column[1] == "Data" and column[2] != "Total":
                acc_temp = acTypeBa if column[4] == "Electronic Fund Transfer" else acTypeIa
                dbi.addTransfer(
                    req,
                    True,
                    acc_temp if floatGaver(column[5]) > 0 else acc,
                    acc if floatGaver(column[5]) > 0 else acc_temp,
                    column[3],
                    column[2],
                    floatGaver(column[5]),
                    0,
                    "",
                    column[4]
                )

            elif column[0] == "Transaction Fees" and column[1] == "Data" and column[2] != "Total":
                dbi.addTransaction(
                    req,
                    True,
                    acc,
                    "",
                    trType,
                    column[4],
                    column[3],
                    column[5],
                    0,
                    0,
                    0,
                    floatGaver(column[9]),
                    column[3] if len(column[3]) > 0 else "",
                    column[6]
                )

            elif column[0] == "Account Information" and column[1] == "Data" and column[2] == "Base Currency":
                forex_fee = column[3]

            elif column[0] == "Trades" and column[1] == "Header":
                if str(column[11])[:8] == "Comm in ":
                    forex_fee = str(column[11])[8:]


def floatGaver(f):
    return round(float(f.replace(",",".")), 4)
