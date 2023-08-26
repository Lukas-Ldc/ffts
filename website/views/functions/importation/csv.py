from io import StringIO
from csv import reader as csvreader
from website.views.functions.dbinterface import add_transaction, add_transfer


def csv_importer(file, table: str, transf_acc: str, acc: str, request, utc: str):
    """Import an FFTS export

    Args:
        file (file): The file that contains the data to import
        table (str): The type of data imported
        transf_acc (str): The account to replace in a transfer (because there is source and destination)
        acc (str): The account that will receive the imported data
        request (HttpRequest): The request made to send the file
        utc (str): The timezone of the data from the imported file
    """

    if file.name.endswith('.csv'):

        # The user wants to import transactions
        if table == "Transactions":
            for column in csvreader(StringIO(file.read().decode('UTF-8')), delimiter=','):

                if len(column) > 0 and column[0] != "Account":
                    print(column[0])
                    add_transaction(
                        request,
                        True,
                        False,
                        utc,
                        acc,
                        column[1],
                        column[2],
                        column[3],
                        column[4],
                        column[5],
                        column[6],
                        column[7],
                        column[8],
                        column[9],
                        column[10],
                        column[11]
                    )

        # The user wants to import transfers
        elif table == "Transfers":
            for column in csvreader(StringIO(file.read().decode('UTF-8')), delimiter=','):

                if len(column) > 0 and not column[0] != "Source":
                    add_transfer(
                        request,
                        True,
                        False,
                        utc,
                        column[0] if transf_acc != column[0] else acc,
                        column[1] if transf_acc != column[1] else acc,
                        column[2],
                        column[3],
                        column[4],
                        column[5],
                        column[6],
                        column[7]
                    )
