import csv, io
import website.views.functions.dbinterface as dbi


def degiro_importer(file, table, trType, acType, acc, req):

    if file.name.endswith('.csv'):

        if table == "Transactions":
            for column in csv.reader(io.StringIO(file.read().decode('UTF-8')), delimiter=','):
                dbi.addTransaction(
                    req, 
                    True, 
                    acc, 
                    column[4], 
                    trType, 
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

        elif table == "Transfers":
            change = False
            for column in csv.reader(io.StringIO(file.read().decode('UTF-8')), delimiter=','):

                if column[5] == "DEPOSIT" or column[5] == "Versement de fonds":
                    dbi.addTransfer(
                        req,
                        True,
                        acType,
                        acc,
                        column[0] + ' ' + column[1],
                        column[7],
                        column[8],
                        0,
                        "",
                        ""
                    )

                elif column[5] == "WITHDRAWAL" or column[5] == "Retrait flatex":
                    dbi.addTransfer(
                        req,
                        True,
                        acc,
                        acType,
                        column[0] + ' ' + column[1],
                        column[7],
                        column[8],
                        0,
                        "",
                        ""
                    )

                elif column[5] == "CHANGE_IN" or column[5] == "Operation de change - Crédit":
                    if change:
                        dbi.modTransaction(
                            req,
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
                        last = dbi.addTransaction(
                            req,
                            True,
                            acc,
                            "",
                            trType,
                            column[0] + ' ' + column[1],
                            "TEMP",
                            column[7],
                            0,
                            column[8],
                            opp(column[6]),
                            0,
                            "",
                            ""
                        )
                        change = True

                elif column[5] == "CHANGE_OUT" or column[5] == "Opération de change - Débit":
                    if change:
                        dbi.modTransaction(
                            req,
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
                        last = dbi.addTransaction(
                            req,
                            True,
                            acc,
                            "",
                            trType,
                            column[0] + ' ' + column[1],
                            column[7],
                            "TEMP",
                            column[8],
                            0,
                            opp(column[6]),
                            0,
                            "",
                            ""
                        )
                        change = True


def opp(n):
    try:
        return round(1 / float(n.replace(",",".").replace("-","")), 4)
    except:
        return 0
