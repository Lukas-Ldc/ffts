import csv, io
import website.views.functions.dbinterface as dbi

def gateio_importer(file, table, trType, acType, acc, req):

    if file.name.endswith('.csv'):

        if table == "Transactions":
            for column in csv.reader(io.StringIO(file.read().decode('UTF-16')), delimiter='\t'):
                dbi.addTransaction(
                    req,
                    True,
                    acc,
                    "",
                    trType,
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
            for column in csv.reader(io.StringIO(file.read().decode('UTF-16')), delimiter='\t'):
                dbi.addTransfer(
                    req,
                    True,
                    column[5] if acType == "Manual" else acType,
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
                        gt = line.split('<td>')[5].split("</td>")[0]

                        dbi.addTransaction(
                            req,
                            True,
                            acc,
                            "",
                            trType,
                            time,
                            coin,
                            "GT",
                            amount,
                            gt,
                            floatRemover(float(amount)/float(gt)),
                            0,
                            "",
                            "Dust",
                        )
                    except: pass


def floatRemover(f):
    if f > 1000:
        return round(f, 2)
    elif f > 100:
        return round(f, 4)
    elif f > 10:
        return round(f, 6)
    elif f > 1:
        return round(f, 8)
    else:
        return round(f, 10)
