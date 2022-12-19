from io import StringIO
from csv import reader as csvreader
from website.views.functions.dbinterface import add_transaction, add_transfer


def gateio_importer(file, table, tr_type, ac_type, acc, req):

    if file.name.endswith('.csv'):

        if table == "Transactions":
            for column in csvreader(StringIO(file.read().decode('UTF-16')), delimiter='\t'):
                add_transaction(
                    req,
                    True,
                    acc,
                    "",
                    tr_type,
                    column[1],
                    column[3].split('/')[1] if column[2] == "Buy" else column[3].split('/')[0],
                    column[3].split('/')[0] if column[2] == "Buy" else column[3].split('/')[1],
                    column[6] if column[2] == "Buy" else column[5],
                    column[5] if column[2] == "Buy" else column[6],
                    column[4],
                    column[7].split(" ")[0],
                    column[7].split(" ")[1],
                    ""
                )

        elif table == "CryptoDeposit":
            for column in csvreader(StringIO(file.read().decode('UTF-16')), delimiter='\t'):
                add_transfer(
                    req,
                    True,
                    column[5] if ac_type == "Manual" else ac_type,
                    acc,
                    column[2],
                    column[3],
                    column[4],
                    0,
                    "",
                    ""
                )

    elif file.name.endswith('.html'):

        if table == "Dust":
            for html in file:

                for line in str(html).split("<tr"):
                    try:
                        time = line.split('<div>')[1].split("</div>")[0]
                        coin = line.split('<td>')[3].split("</td>")[0]
                        amount = line.split('<td>')[4].split("</td>")[0]
                        gtt = line.split('<td>')[5].split("</td>")[0]

                        add_transaction(
                            req,
                            True,
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


def float_remover(number):
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
