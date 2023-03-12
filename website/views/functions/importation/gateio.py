from io import StringIO
from csv import reader as csvreader
from website.views.functions.dbinterface import add_transaction, add_transfer


def gateio_importer(file, table: str, tr_type: str, transf_acc: str, acc: str, request):
    """Import an Gate.io export

    Args:
        file (file): The file that contains the data to import
        table (str): The type of data imported
        tr_type (str): The type of transaction
        transf_acc (str): The account linked to the transfer
        acc (str): The account that will receive the imported data
        request (HttpRequest): The request made to send the file
    """

    if file.name.endswith('.csv'):

        # The user wants to add transactions
        if table == "Transactions":
            for column in csvreader(StringIO(file.read().decode('UTF-16')), delimiter='\t'):
                add_transaction(
                    request,
                    True,
                    False,
                    acc,
                    "",
                    tr_type,
                    column[2],
                    column[5].split('/')[1] if column[3] == "Buy" else column[5].split('/')[0],
                    column[5].split('/')[0] if column[3] == "Buy" else column[5].split('/')[1],
                    column[8] if column[3] == "Buy" else column[7],
                    column[7] if column[3] == "Buy" else column[8],
                    column[6],
                    column[9].split(" ")[0],
                    column[9].split(" ")[1],
                    ""
                )

        # The user wants to add deposits of crypto
        elif table == "CryptoDeposit":
            for column in csvreader(StringIO(file.read().decode('UTF-16')), delimiter='\t'):
                add_transfer(
                    request,
                    True,
                    False,
                    acc,
                    column[5] if transf_acc == "Manual" else transf_acc,
                    acc,
                    column[2],
                    column[3],
                    column[4],
                    0,
                    "",
                    ""
                )

    elif file.name.endswith('.html'):

        # The user wants to import dust
        if table == "Dust":

            for html in file:
                # For each dust transaction
                for line in str(html).split("<tr"):
                    try:
                        # Extracting the data from the HTML
                        time = line.split('<div>')[1].split("</div>")[0]
                        coin = line.split('<td>')[3].split("</td>")[0]
                        amount = line.split('<td>')[4].split("</td>")[0]
                        gtt = line.split('<td>')[5].split("</td>")[0]

                        add_transaction(
                            request,
                            True,
                            False,
                            acc,
                            "",
                            tr_type,
                            time,
                            coin,
                            "GT",
                            amount,
                            gtt,
                            float_remover(float(amount) / float(gtt)),
                            0,
                            "",
                            "Dust",
                        )
                    except IndexError:
                        pass


def float_remover(number: float):
    """Depending on the size of the number, limits the number of digits after the decimal point

    Args:
        number (float): The number to clean

    Returns:
        float: The cleaned number
    """
    if number > 1000:
        return round(number, 2)
    elif number > 100:
        return round(number, 4)
    elif number > 10:
        return round(number, 6)
    elif number > 1:
        return round(number, 8)
    else:
        return round(number, 10)
