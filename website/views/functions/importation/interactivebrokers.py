from io import StringIO
from csv import reader as csvreader
from website.models import Account
from website.views.functions.dbinterface import add_transaction, add_transfer


def ib_importer(file, tr_type, ac_type_ba, ac_type_ia, acc, req):

    if file.name.endswith('.csv'):

        forex_fee = str(Account.objects.all().get(unique__exact=acc).unit).split(",")[0]

        for column in csvreader(StringIO(file.read().decode('UTF-8')), delimiter=','):

            if column[0] == "Trades" and column[1] == "Data" and column[2] == "Order" and column[3] == "Forex":
                add_transaction(
                    req,
                    True,
                    acc,
                    "",
                    tr_type,
                    str(column[6]).replace(",", ""),
                    str(column[5]).split(".")[1] if float_gaver(column[7]) > 0 else str(column[5]).split(".")[0],
                    str(column[5]).split(".")[0] if float_gaver(column[7]) > 0 else str(column[5]).split(".")[1],
                    float_gaver(column[10]) if float_gaver(column[7]) > 0 else float_gaver(column[7]),
                    float_gaver(column[7]) if float_gaver(column[7]) > 0 else float_gaver(column[10]),
                    float_gaver(column[8]),
                    float_gaver(column[11]),
                    forex_fee,
                    column[3]
                )

            elif column[0] == "Trades" and column[1] == "Data" and column[2] == "Order":
                add_transaction(
                    req,
                    True,
                    acc,
                    "",
                    tr_type,
                    str(column[6]).replace(",", ""),
                    column[4] if float_gaver(column[7]) > 0 else column[5],
                    column[5] if float_gaver(column[7]) > 0 else column[4],
                    float_gaver(column[10]) if float_gaver(column[7]) > 0 else float_gaver(column[7]),
                    float_gaver(column[7]) if float_gaver(column[7]) > 0 else float_gaver(column[10]),
                    float_gaver(column[8]),
                    float_gaver(column[11]),
                    column[4] if len(column[4]) > 0 else "",
                    column[3]
                )

            elif column[0] == "Deposits & Withdrawals" and column[1] == "Data" and column[2] != "Total":
                acc_temp = ac_type_ba if column[4] == "Electronic Fund Transfer" else ac_type_ia
                add_transfer(
                    req,
                    True,
                    acc_temp if float_gaver(column[5]) > 0 else acc,
                    acc if float_gaver(column[5]) > 0 else acc_temp,
                    column[3],
                    column[2],
                    float_gaver(column[5]),
                    0,
                    "",
                    column[4]
                )

            elif column[0] == "Transaction Fees" and column[1] == "Data" and column[2] != "Total":
                add_transaction(
                    req,
                    True,
                    acc,
                    "",
                    tr_type,
                    column[4],
                    column[3],
                    column[5],
                    0,
                    0,
                    0,
                    float_gaver(column[9]),
                    column[3] if len(column[3]) > 0 else "",
                    column[6]
                )

            elif column[0] == "Account Information" and column[1] == "Data" and column[2] == "Base Currency":
                forex_fee = column[3]

            elif column[0] == "Trades" and column[1] == "Header":
                if str(column[11])[:8] == "Comm in ":
                    forex_fee = str(column[11])[8:]


def float_gaver(number):
    return round(float(number.replace(",", "")), 4)
