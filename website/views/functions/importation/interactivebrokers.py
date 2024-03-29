from io import StringIO
from csv import reader as csvreader
from website.views.functions.dbinterface import add_transaction, add_transfer
from website.views.functions.data_functions import strn


def ib_importer(file, tr_type: str, bank_acc: str, ib_acc: str, acc: str, request, utc: str):
    """Import an InteractiveBrokers export

    Args:
        file (file): The file that contains the data to import
        tr_type (str): The type of transaction
        bank_acc (str): The account linked to the withdrawals & deposits
        ib_acc (str): Internal IB account and making internal transfers
        acc (str): The account that will receive the imported data
        request (HttpRequest): The request made to send the file
        utc (str): The timezone of the data from the imported file
    """

    if file.name.endswith('.csv'):

        forex_fee_unit = None

        for column in csvreader(StringIO(file.read().decode('UTF-8')), delimiter=','):

            # Importation of a change operation
            if column[0] == "Trades" and column[1] == "Data" and column[2] == "Order" and column[3] == "Forex":
                column[7] = strn(column[7], "", True)

                add_transaction(
                    request,
                    True,
                    False,
                    utc,
                    acc,
                    "",
                    tr_type,
                    strn(column[6], ""),
                    str(column[5]).split(".")[1] if column[7] > 0 else str(column[5]).split(".")[0],
                    str(column[5]).split(".")[0] if column[7] > 0 else str(column[5]).split(".")[1],
                    strn(column[10], "") if column[7] > 0 else column[7],
                    column[7] if column[7] > 0 else strn(column[10], ""),
                    round(1 / strn(column[8], "", True), 4) if column[7] > 0 else strn(column[8], ""),
                    strn(column[11], ""),
                    str(column[5]).split(".")[0] if forex_fee_unit is None else forex_fee_unit,
                    column[3]
                )

            # Importation of a transaction (not a change operation)
            elif column[0] == "Trades" and column[1] == "Data" and column[2] == "Order":
                column[7] = strn(column[7], "", True)

                add_transaction(
                    request,
                    True,
                    False,
                    utc,
                    acc,
                    "",
                    tr_type,
                    strn(column[6], ""),
                    column[4] if column[7] > 0 else column[5],
                    column[5] if column[7] > 0 else column[4],
                    strn(column[10], "") if column[7] > 0 else column[7],
                    column[7] if column[7] > 0 else strn(column[10], ""),
                    strn(column[8], ""),
                    strn(column[11], ""),
                    column[4] if len(column[4]) > 0 else "",
                    column[3]
                )

            # Importation of a deposit / withdrawal
            elif column[0] == "Deposits & Withdrawals" and column[1] == "Data" and column[2] != "Total":
                acc_temp = bank_acc if column[4] == "Electronic Fund Transfer" else ib_acc
                add_transfer(
                    request,
                    True,
                    False,
                    utc,
                    acc_temp if float(column[5]) > 0 else acc,
                    acc if float(column[5]) > 0 else acc_temp,
                    column[3],
                    column[2],
                    strn(column[5], ""),
                    0,
                    "",
                    column[4]
                )

            # Importation of transaction fees
            elif column[0] == "Transaction Fees" and column[1] == "Data" and column[2] != "Total":
                add_transaction(
                    request,
                    True,
                    False,
                    utc,
                    acc,
                    "",
                    tr_type,
                    column[4],
                    column[3],
                    column[5],
                    0,
                    0,
                    0,
                    strn(column[9], ""),
                    column[3] if len(column[3]) > 0 else "",
                    column[6]
                )

            # Extracting the forex fee unit
            elif column[0] == "Account Information" and column[1] == "Data" and column[2] == "Base Currency":
                forex_fee_unit = column[3]

            elif column[0] == "Trades" and column[1] == "Header":
                if str(column[11])[:8] == "Comm in ":
                    forex_fee_unit = str(column[11])[8:]
