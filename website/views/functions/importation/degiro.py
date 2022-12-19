from io import StringIO
from csv import reader as csvreader
from website.views.functions.dbinterface import add_transaction, add_transfer, mod_transaction


def degiro_importer(file, table, tr_type, ac_type, acc, req):

    if file.name.endswith('.csv'):

        if table == "Transactions":
            for column in csvreader(StringIO(file.read().decode('UTF-8')), delimiter=','):
                add_transaction(
                    req,
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

        elif table == "Transfers":
            change = False
            for column in csvreader(StringIO(file.read().decode('UTF-8')), delimiter=','):

                if column[5] == "DEPOSIT" or column[5] == "Versement de fonds":
                    add_transfer(
                        req,
                        True,
                        ac_type,
                        acc,
                        column[0] + ' ' + column[1],
                        column[7],
                        column[8],
                        0,
                        "",
                        ""
                    )

                elif column[5] == "WITHDRAWAL" or column[5] == "Retrait flatex":
                    add_transfer(
                        req,
                        True,
                        acc,
                        ac_type,
                        column[0] + ' ' + column[1],
                        column[7],
                        column[8],
                        0,
                        "",
                        ""
                    )

                elif column[5] == "CHANGE_IN" or column[5] == "Operation de change - Crédit":
                    if change:
                        mod_transaction(
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
                        last = add_transaction(
                            req,
                            True,
                            acc,
                            "",
                            tr_type,
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
                        mod_transaction(
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
                        last = add_transaction(
                            req,
                            True,
                            acc,
                            "",
                            tr_type,
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


def opp(number):
    try:
        return round(1 / float(number.replace(",", ".").replace("-", "")), 4)
    except ZeroDivisionError:
        return 0
