from io import StringIO
from csv import reader as csvreader
from website.views.functions.dbinterface import add_transaction, add_transfer, mod_transaction
from website.views.functions.data_functions import strn, opposite


def degiro_importer(file, table: str, tr_type: str, bank_acc: str, acc: str, request, utc: str):
    """Import an FFTS export

    Args:
        file (file): The file that contains the data to import
        table (str): The type of data imported
        tr_type (str): The type of transaction
        bank_acc (str): The bank account used for withdrawal & deposits
        acc (str): The account that will receive the imported data
        request (HttpRequest): The request made to send the file
        utc (str): The timezone of the data from the imported file
    """

    if file.name.endswith('.csv'):

        # The user wants to import transactions
        if table == "Transactions":
            for column in csvreader(StringIO(file.read().decode('UTF-8')), delimiter=','):

                if len(column) > 0 and column[0][0].isdigit():
                    add_transaction(
                        request,
                        True,
                        True,
                        utc,
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
                        True,
                        utc,
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
                        True,
                        utc,
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
                            True,
                            utc,
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
                            True,
                            utc,
                            acc,
                            "",
                            tr_type,
                            column[0] + ' ' + column[1],
                            "TEMP",
                            column[7],
                            0,
                            column[8],
                            opposite(strn(column[6], ".", True), 4),
                            0,
                            "",
                            ""
                        )
                        change = True

                elif column[5] == "CHANGE_OUT" or column[5] == "Opération de change - Débit":
                    if change:
                        mod_transaction(
                            request,
                            True,
                            utc,
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
                            True,
                            utc,
                            acc,
                            "",
                            tr_type,
                            column[0] + ' ' + column[1],
                            column[7],
                            "TEMP",
                            column[8],
                            0,
                            opposite(strn(column[6], ".", True), 4),
                            0,
                            "",
                            ""
                        )
                        change = True
