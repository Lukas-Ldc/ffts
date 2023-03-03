from io import StringIO
from csv import reader as csvreader
from website.views.functions.dbinterface import add_transaction, add_transfer, mod_transaction


def degiro_importer(file, table: str, tr_type: str, bank_acc: str, acc: str, request):
    """Import an FFTS export

    Args:
        file (file): The file that contains the data to import
        table (str): The type of data imported
        tr_type (str): The type of transaction
        bank_acc (str): The bank account used for withdrawal & deposits
        acc (str): The account that will receive the imported data
        request (HttpRequest): The request made to send the file
    """

    if file.name.endswith('.csv'):

        # The user wants to import transactions
        if table == "Transactions":
            for column in csvreader(StringIO(file.read().decode('UTF-8')), delimiter=','):
                add_transaction(
                    request,
                    True,
                    acc,
                    column[4],
                    tr_type,
                    column[0] + ' ' + column[1],
                    column[10] if float(column[6]) > 0 else column[2],
                    column[2] if float(column[6]) > 0 else column[10],
                    column[9] if float(column[6]) > 0 else column[6],
                    column[6] if float(column[6]) > 0 else column[9],
                    column[7],
                    column[14],
                    column[15] if len(column[15]) > 0 else "",
                    ""
                )

        # The user wants to import transfers
        elif table == "Transfers":
            change = False  # First change operation found, waiting for the second

            for column in csvreader(StringIO(file.read().decode('UTF-8')), delimiter=','):

                # Deposit
                if column[5] == "DEPOSIT" or column[5] == "Versement de fonds":
                    add_transfer(
                        request,
                        True,
                        bank_acc,
                        acc,
                        column[0] + ' ' + column[1],
                        column[7],
                        column[8],
                        0,
                        "",
                        ""
                    )

                # Withdrawal
                elif column[5] == "WITHDRAWAL" or column[5] == "Retrait flatex":
                    add_transfer(
                        request,
                        True,
                        acc,
                        bank_acc,
                        column[0] + ' ' + column[1],
                        column[7],
                        column[8],
                        0,
                        "",
                        ""
                    )

                # Change operations takes to 2 lines in the CSV that need to be united

                elif column[5] == "CHANGE_IN" or column[5] == "Operation de change - Crédit":
                    if change:
                        mod_transaction(
                            request,
                            last.id,
                            None,
                            None,
                            None,
                            None,
                            column[7],
                            None,
                            column[8],
                            None,
                            None,
                            None,
                            None
                        )
                        change = False

                    else:
                        last = add_transaction(
                            request,
                            True,
                            acc,
                            "",
                            tr_type,
                            column[0] + ' ' + column[1],
                            "TEMP",
                            column[7],
                            0,
                            column[8],
                            change_price_giver(column[6]),
                            0,
                            "",
                            ""
                        )
                        change = True

                elif column[5] == "CHANGE_OUT" or column[5] == "Opération de change - Débit":
                    if change:
                        mod_transaction(
                            request,
                            last.id,
                            None,
                            None,
                            None,
                            column[7],
                            None,
                            column[8],
                            None,
                            None,
                            None,
                            None,
                            None
                        )
                        change = False

                    else:
                        last = add_transaction(
                            request,
                            True,
                            acc,
                            "",
                            tr_type,
                            column[0] + ' ' + column[1],
                            column[7],
                            "TEMP",
                            column[8],
                            0,
                            change_price_giver(column[6]),
                            0,
                            "",
                            ""
                        )
                        change = True


def change_price_giver(number: str):
    """Give the price for a change operation.
    Cleans the string and takes the opposite.

    Args:
        number (str): The basic price (inverted)

    Returns:
        float: The new price
    """
    try:
        return round(1 / float(number.replace(",", ".").replace("-", "")), 4)
    except ZeroDivisionError:
        return 0
