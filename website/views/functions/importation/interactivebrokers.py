from io import StringIO
from csv import reader as csvreader
from website.views.functions.dbinterface import add_transaction, add_transfer


def ib_importer(file, tr_type: str, bank_acc: str, ib_acc: str, acc: str, request):
    """Import an InteractiveBrokers export

    Args:
        file (file): The file that contains the data to import
        tr_type (str): The type of transaction
        bank_acc (str): The account linked to the withdrawals & deposits
        ib_acc (str): Internal IB account and making internal transfers
        acc (str): The account that will receive the imported data
        request (HttpRequest): The request made to send the file
    """

    if file.name.endswith('.csv'):

        forex_fee_unit = None

        for column in csvreader(StringIO(file.read().decode('UTF-8')), delimiter=','):

            # Importation of a change operation
            if column[0] == "Trades" and column[1] == "Data" and column[2] == "Order" and column[3] == "Forex":
                add_transaction(
                    request,
                    True,
                    False,
                    acc,
                    "",
                    tr_type,
                    str(column[6]).replace(",", ""),
                    str(column[5]).split(".")[1] if float_gaver(column[7]) > 0 else str(column[5]).split(".")[0],
                    str(column[5]).split(".")[0] if float_gaver(column[7]) > 0 else str(column[5]).split(".")[1],
                    float_gaver(column[10]) if float_gaver(column[7]) > 0 else float_gaver(column[7]),
                    float_gaver(column[7]) if float_gaver(column[7]) > 0 else float_gaver(column[10]),
                    float_gaver(1 / float(column[8])) if float_gaver(column[7]) > 0 else float_gaver(column[8]),
                    float_gaver(column[11]),
                    str(column[5]).split(".")[0] if forex_fee_unit is None else forex_fee_unit,
                    column[3]
                )

            # Importation of a transaction (not a change operation)
            elif column[0] == "Trades" and column[1] == "Data" and column[2] == "Order":
                add_transaction(
                    request,
                    True,
                    False,
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

            # Importation of a deposit / withdrawal
            elif column[0] == "Deposits & Withdrawals" and column[1] == "Data" and column[2] != "Total":
                acc_temp = bank_acc if column[4] == "Electronic Fund Transfer" else ib_acc
                add_transfer(
                    request,
                    True,
                    False,
                    acc_temp if float_gaver(column[5]) > 0 else acc,
                    acc if float_gaver(column[5]) > 0 else acc_temp,
                    column[3],
                    column[2],
                    float_gaver(column[5]),
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

            # Extracting the forex fee unit
            elif column[0] == "Account Information" and column[1] == "Data" and column[2] == "Base Currency":
                forex_fee_unit = column[3]

            elif column[0] == "Trades" and column[1] == "Header":
                if str(column[11])[:8] == "Comm in ":
                    forex_fee_unit = str(column[11])[8:]


def float_gaver(number: str):
    """Returns a float from a string with a limited precision.

    Args:
        number (str): The number to convert

    Returns:
        float: The correct number
    """
    return round(float(str(number).replace(",", "")), 4)
