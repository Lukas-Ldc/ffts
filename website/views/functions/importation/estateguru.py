from io import StringIO
from csv import reader as csvreader
from website.views.functions.dbinterface import add_transaction, add_transfer


def estateguru_importer(file, bank_acc: str, acc: str, req):
    """Import an EstateGuru export

    Args:
        file (file): The file that contains the data to import
        bank_acc (str): The account linked to the withdrawals & deposits
        acc (str): The account that will receive the imported data
        req (HttpRequest): The request made to send the file
    """

    if file.name.endswith('.csv'):

        for column in csvreader(StringIO(file.read().decode('UTF-8')), delimiter=','):

            # Adding a deposit or a withdrawal
            # Not sure about "Withdrawal" keyword, to confirm (never made one)
            if column[6] == "Approved" and column[5] == "Deposit" or column[5] == "Withdrawal":
                add_transfer(
                    req,
                    True,
                    True,
                    bank_acc if column[5] == "Deposit" else acc,
                    acc if column[5] == "Deposit" else bank_acc,
                    column[3],
                    column[10],
                    column[8],
                    0,
                    "",
                    ""
                )

            # Adding a transaction
            elif column[6] == "Approved":
                add_transaction(
                    req,
                    True,
                    True,
                    acc,
                    "",
                    column[5],
                    column[3],
                    column[10] if column[5].startswith("Investment") else column[2],
                    column[2] if column[5].startswith("Investment") else column[10],
                    0 if column[5] in ["Interest", "Indemnity"] else column[8],
                    column[8],
                    "1",
                    "0",
                    "",
                    ""
                )
