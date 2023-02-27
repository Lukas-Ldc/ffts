from io import StringIO
from csv import reader as csvreader
from website.views.functions.dbinterface import add_transaction, add_transfer


def estateguru_importer(file, bk_acc, acc, req):

    if file.name.endswith('.csv'):

        for column in csvreader(StringIO(file.read().decode('UTF-8')), delimiter=','):
            if column[6] == "Approved" and column[5] == "Deposit" or column[5] == "Withdrawal":
                add_transfer(  # Not sure about "Withdrawal" keyword, to confirm (never made one)
                    req,
                    True,
                    bk_acc if column[5] == "Deposit" else acc,
                    acc if column[5] == "Deposit" else bk_acc,
                    column[3],
                    column[10],
                    column[8],
                    0,
                    "",
                    ""
                )

            elif column[6] == "Approved":
                add_transaction(
                    req,
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
