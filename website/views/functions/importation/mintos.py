from io import StringIO
from csv import reader as csvreader
from website.views.functions.dbinterface import add_transaction, add_transfer


def mintos_importer(file, bank_acc: str, acc: str, req, utc: str):
    """Import an Mintos export

    Args:
        file (file): The file that contains the data to import
        bank_acc (str): The account linked to the withdrawals & deposits
        acc (str): The account that will receive the imported data
        req (HttpRequest): The request made to send the file
        utc (str): The timezone of the data from the imported file
    """

    if file.name.endswith('.csv'):

        for column in csvreader(StringIO(file.read().decode('UTF-8')), delimiter=','):

            if column[6] == "Investment" or column[6] == "Principal" or column[6] == "Interest":
                note = column[2].split(" ")[1]
                loan = column[2].split("(")[1].split(")")[0].split(" ")
                loan = loan[0] if "-" in loan[0] else loan[1]
                amount = round(float(column[3]), 15)

                add_transaction(
                    request=req,
                    antidup=True,
                    dayfirst=False,
                    utc=utc,
                    account=acc,
                    market=None,
                    tyype=column[6],
                    date=column[0],
                    iinput=column[5] if float(column[3]) < 0 else note,
                    output=note if float(column[3]) < 0 else column[5],
                    amount_in=amount if column[6] != "Interest" else 0,
                    amount_out=amount,
                    price=None,
                    fee=None,
                    fee_unit=None,
                    comment=loan,
                    antidupcom=True
                )

            elif column[6] == "Tax" or column[6] == "Fee":
                if column[6] == "Tax":
                    note = column[2].split(" ")[1]
                    loan = column[2].split("(")[1].split(")")[0].split(" ")
                    loan = loan[0] if "-" in loan[0] else loan[1]
                else:
                    note, loan = "Mintos", ""

                add_transaction(
                    request=req,
                    antidup=True,
                    dayfirst=False,
                    utc=utc,
                    account=acc,
                    market=None,
                    tyype=column[6],
                    date=column[0],
                    iinput=column[5],
                    output=note,
                    amount_in=round(float(column[3]), 15),
                    amount_out=0,
                    price=None,
                    fee=None,
                    fee_unit=None,
                    comment=loan,
                    antidupcom=True
                )

            elif column[6] == "Deposit" or column[6] == "Withdrawal":

                add_transfer(
                    request=req,
                    antidup=True,
                    dayfirst=False,
                    utc=utc,
                    source=bank_acc if "deposit" in column[6].lower() else acc,
                    destination=acc if "deposit" in column[6].lower() else bank_acc,
                    date=column[0],
                    unit=column[5],
                    amount=round(float(column[3]), 15),
                    fee=0,
                    fee_unit=None,
                    comment=None
                )
