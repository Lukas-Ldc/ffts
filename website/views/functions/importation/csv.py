import csv, io
import website.views.functions.dbinterface as dbi

def csv_importer(file, table, old, acc, req):

    if file.name.endswith('.csv'):

        if table == "Transactions":
            for column in csv.reader(io.StringIO(file.read().decode('UTF-8')), delimiter=','):
                dbi.addTransaction(
                    req, 
                    True, 
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

        elif table == "Transfers":
            for column in csv.reader(io.StringIO(file.read().decode('UTF-8')), delimiter=','):
                dbi.addTransfer(
                    req, 
                    True, 
                    column[0] if old != column[0] else acc,
                    column[1] if old != column[1] else acc,
                    column[2], 
                    column[3], 
                    column[4], 
                    column[5], 
                    column[6], 
                    column[7]
                )
