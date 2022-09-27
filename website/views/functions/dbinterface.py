from dateutil import parser
from django.db.models import Q
from django.http import HttpRequest
from website.models import Transaction, Transfer, Account, Standard

#Value used to clear a field during a modification
empty = "0"

def addAccount(req: HttpRequest, p_nam, p_typ, p_grp, p_unt, p_gmt, p_cmt):
    #Used to add a new account in the database.
    #The first parameter is the user request and the others are the fields of an account (cf. models.py, except unique and user).
    #Return False or the account added.
    
    #Creating the account
    new_acc = Account.objects.create(
        unique = '.',
        name = normalData(p_nam),
        type = accTypeChecker(p_typ),
        user = req.user,
        group = normalData(p_grp),
        unit = normalData(p_unt),
        gmt = int(p_gmt) if emptyChecker(p_gmt) else 0,
        comment = normalData(p_cmt)
    )
    return new_acc


def addTransaction(req: HttpRequest, dup: bool, p_acc, p_mkt, p_typ, p_dat, p_iin, p_out, p_aIn, p_aOu, p_prc, p_fee, p_feU, p_cmt):
    #Used to add a new transcation in the database.
    #The first parameter is the user request and the others are the fields of a transaction (cf. models.py).
    #Return False or the transaction added.

    #Getting the user account
    try: the_account = Account.objects.all().get(user__exact=req.user, unique__exact=p_acc)
    except: return False

    #Getting a possible duplicate transaction (account, date, input, output and amounts)
    try: old_tr = Transaction.objects.all().filter(account__exact=the_account, date__exact=dateChecker(p_dat), input__exact=normalData(p_iin), output__exact=normalData(p_out), amountIn__exact=correctNumber(p_aIn), amountOut__exact=correctNumber(p_aOu))[0]
    except: old_tr = False

    #If duplicate, update transaction
    if old_tr and dup:
        old_tr.market = normalData(p_mkt)
        old_tr.type = trTypeChecker(p_typ)
        old_tr.price = correctNumber(p_prc)
        old_tr.fee = correctNumber(p_fee)
        old_tr.feeUnit = normalData(p_feU)
        old_tr.comment = normalData(p_cmt)
        old_tr.save()
        return old_tr

    #Else add the new transaction
    else:
        new_tf = Transaction.objects.create(
            account = the_account, 
            market = normalData(p_mkt),
            type = trTypeChecker(p_typ),
            date = dateChecker(p_dat),
            input = normalData(p_iin),
            output = normalData(p_out),
            amountIn = correctNumber(p_aIn),
            amountOut = correctNumber(p_aOu),
            price = correctNumber(p_prc),
            fee = correctNumber(p_fee),
            feeUnit = normalData(p_feU),
            comment = normalData(p_cmt)
        )
        return new_tf


def addTransfer(req: HttpRequest, dup: bool, p_src, p_dst, p_dat, p_uni, p_amt, p_fee, p_feU, p_cmt):
    #Used to add a new transfer in the database.
    #The first parameter is the user request and the others are the fields of a transfer (cf. models.py).
    #Return False or the transfer added.

    #Getting the accounts
    try: the_source = Account.objects.all().get(unique__exact=p_src)
    except: return False
    try: the_destination = Account.objects.all().get(unique__exact=p_dst)
    except: return False

    #Verifying if one of the accounts belongs to the user
    if not the_source.user == req.user and not the_destination.user == req.user:
        return False
    
    #Getting a possible duplicate transfer (source, destination, date, unit, amount)
    try: old_tf = Transfer.objects.all().filter(source__exact=the_source, destination__exact=the_destination, date__exact=dateChecker(p_dat), unit__exact=normalData(p_uni), amount__exact=correctNumber(p_amt))[0]
    except: old_tf = False

    #If duplicate, update transfer
    if old_tf and dup:
        old_tf.fee = correctNumber(p_fee)
        old_tf.feeUnit = normalData(p_feU)
        old_tf.comment = normalData(p_cmt)
        old_tf.save()
        return old_tf
    
    #Else add the new transfer
    else:
        new_tr = Transfer.objects.create(
            source = the_source, 
            destination = the_destination, 
            date = dateChecker(p_dat), 
            unit = normalData(p_uni), 
            amount = correctNumber(p_amt), 
            fee = correctNumber(p_fee), 
            feeUnit = normalData(p_feU), 
            comment = normalData(p_cmt)
        )
        return new_tr


def modAccount(req: HttpRequest, p_nam, p_typ, p_grp, p_unt, p_gmt, p_cmt):
    #Used to modify an account in the database.
    #The first parameter is the user request and the others are the fields of an account (cf. models.py, except unique and user).
    #Return False or the account modified.
    
    #Getting the account
    try: the_acc = Account.objects.all().get(user__exact=req.user, name__exact=p_nam)
    except: return False

    #Modification of the account
    if emptyChecker(p_typ): the_acc.type = "" if str(p_typ) == empty else accTypeChecker(p_typ)
    if emptyChecker(p_grp): the_acc.group = "" if str(p_grp) == empty else normalData(p_grp)
    if emptyChecker(p_unt): the_acc.unit = "" if str(p_unt) == empty else normalData(p_unt)
    if emptyChecker(p_gmt): the_acc.gmt = 0 if str(p_gmt) == empty else int(p_gmt)
    if emptyChecker(p_cmt): the_acc.comment = "" if str(p_cmt) == empty else normalData(p_cmt)
    the_acc.save()
    return the_acc


def modTransaction(req: HttpRequest, p_id, p_mkt, p_typ, p_dat, p_iin, p_out, p_aIn, p_aOu, p_prc, p_fee, p_feU, p_cmt):
    #Used to modify a transcation in the database.
    #The first parameter is the user request, the second is the ID and the others are the fields of a transaction (cf. models.py, account excluded).
    #Return False or the transaction modified.
    
    #Getting the transaction
    try: the_tr = Transaction.objects.all().get(id__exact=p_id)
    except: return False
    
    #Verifying if the transaction belongs to the user
    try: the_account = Account.objects.all().get(user__exact=req.user, unique__exact=the_tr.account.unique)
    except: return False
    
    #Modification of the transaction
    if emptyChecker(p_mkt): the_tr.market = "" if str(p_mkt) == empty else normalData(p_mkt)
    if emptyChecker(p_typ): the_tr.type = "" if str(p_typ) == empty else trTypeChecker(p_typ)
    if emptyChecker(p_dat): the_tr.date = the_tr.date if str(p_dat) == empty else dateChecker(p_dat)
    if emptyChecker(p_iin): the_tr.input = the_tr.input if str(p_iin) == empty else normalData(p_iin)
    if emptyChecker(p_out): the_tr.output = the_tr.output if str(p_out) == empty else normalData(p_out)
    if emptyChecker(p_aIn): the_tr.amountIn = the_tr.amountIn if str(p_aIn) == empty else correctNumber(p_aIn)
    if emptyChecker(p_aOu): the_tr.amountOut = the_tr.amountOut if str(p_aOu) == empty else correctNumber(p_aOu)
    if emptyChecker(p_prc): the_tr.price = 0 if str(p_prc) == empty else correctNumber(p_prc)
    if emptyChecker(p_fee): the_tr.fee = 0 if str(p_fee) == empty else correctNumber(p_fee)
    if emptyChecker(p_feU): the_tr.feeUnit = "" if str(p_feU) == empty else normalData(p_feU)
    if emptyChecker(p_cmt): the_tr.comment = "" if str(p_cmt) == empty else normalData(p_cmt)
    the_tr.save()
    return the_tr


def modTransfer(req: HttpRequest, p_id, p_src, p_dst, p_dat, p_uni, p_amt, p_fee, p_feU, p_cmt):
    #Used to modify a transfer in the database.
    #The first parameter is the user request, the second is the ID and the others are the fields of a transfer (cf. models.py, account excluded).
    #Return False or the transfer modified.

    #Getting the transfer
    try: the_tf = Transfer.objects.all().get(id__exact=p_id)
    except: return False

    #Getting the accounts
    try: the_source = Account.objects.all().get(unique__exact=the_tf.source.unique)
    except: return False
    try: the_destination = Account.objects.all().get(unique__exact=the_tf.destination.unique)
    except: return False
    
    #Verifying if one of the accounts belongs to the user
    if not the_source.user == req.user and not the_destination.user == req.user:
        return False
    
    #Verifying if with the news accounts one of them still belongs to the user
    if emptyChecker(p_src):
        try: new_source = Account.objects.all().get(unique__exact=p_src)
        except: return False
    else: new_source = the_source

    if emptyChecker(p_dst):
        try: new_destination = Account.objects.all().get(unique__exact=p_dst)
        except: return False
    else: new_destination = the_destination

    if not new_source.user == req.user and not new_destination.user == req.user:
        return False
    
    #Modification of the transfer
    if emptyChecker(p_src): the_tf.source = the_tf.source if str(p_src) == empty else new_source
    if emptyChecker(p_dst): the_tf.destination = the_tf.destination if str(p_dst) == empty else new_destination
    if emptyChecker(p_dat): the_tf.date = the_tf.date if str(p_dat) == empty else dateChecker(p_dat)
    if emptyChecker(p_uni): the_tf.unit = the_tf.unit if str(p_uni) == empty else correctNumber(p_uni)
    if emptyChecker(p_amt): the_tf.amount = the_tf.amount if str(p_amt) == empty else correctNumber(p_amt)
    if emptyChecker(p_fee): the_tf.fee = 0 if str(p_fee) == empty else correctNumber(p_fee)
    if emptyChecker(p_feU): the_tf.feeUnit = "" if str(p_feU) == empty else normalData(p_feU)
    if emptyChecker(p_cmt): the_tf.comment = "" if str(p_cmt) == empty else normalData(p_cmt)
    the_tf.save()
    return the_tf


def delAccount(req: HttpRequest, p_nam):
    #Used to delete an account in the database.
    #The first parameter is the user request and the second is the name.
    #Return False or True.

    #Deleting the account
    the_acc = Account.objects.all().filter(user__exact=req.user, name__exact=p_nam).delete()
    return True


def delTransaction(req: HttpRequest, p_id):
    #Used to delete a transcation in the database.
    #The first parameter is the user request and the second is the ID.
    #Return False or True.

    #Getting the transaction
    try: the_tr = Transaction.objects.all().get(id__exact=p_id)
    except: return False

    #Verifying if the transaction belongs to the user
    try: the_account = Account.objects.all().get(user__exact=req.user, unique__exact=the_tr.account.unique)
    except: return False

    #Deleting transaction
    Transaction.objects.all().filter(account__exact=the_account, id__exact=p_id).delete()
    return True


def delTransfer(req: HttpRequest, p_id):
    #Used to delete a transfer in the database.
    #The first parameter is the user request and the second is the ID.
    #Return False or True.

    #Getting the transfer
    try: the_tf = Transfer.objects.all().get(id__exact=p_id)
    except: return False

    #Getting the accounts
    try: the_source = Account.objects.all().get(unique__exact=the_tf.source.unique)
    except: return False
    try: the_destination = Account.objects.all().get(unique__exact=the_tf.destination.unique)
    except: return False
    
    #Verifying if one of the accounts belongs to the user
    if not the_source.user == req.user and not the_destination.user == req.user:
        return False

    #Deleting transfer
    Transfer.objects.all().filter(Q(id__exact=p_id), Q(source__exact=the_source) | Q(destination__exact=the_destination)).delete()
    return True


def emptyChecker(d):
    #Verifiy if the variable is not empty
    if d is not None:
        if len(str(d)) > 0:
            return True
    return False


def accTypeChecker(type):
    #Normalise the type for a transaction

    if Standard.objects.all().filter(type__exact='AccountType', name__exact=type).exists():
        return type
    return str("")


def trTypeChecker(type):
    #Normalise the type for a transaction

    if Standard.objects.all().filter(type__exact='TransactionType', name__exact=type).exists():
        return type
    return str("")


def dateChecker(d):
    #Normalise the date
    
    return parser.parse(d).isoformat()


def correctNumber(nb):
    #Normalise the number
    if emptyChecker(nb):
        return float(str(nb).replace(",",".").replace("-",""))
    return 0


def normalData(d):
    #Normalise basic data (not doing anything)

    return str(d)
