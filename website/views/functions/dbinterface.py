from dateutil import parser
from django.db.models import Q
from django.http import HttpRequest
from website.models import Transaction, Transfer, Account, Standard

# Value used to clear a field during a modification
EMPTY = "0"


def add_account(req: HttpRequest, p_nam, p_typ, p_grp, p_unt, p_gmt, p_cmt):
    # Used to add a new account in the database.
    # The first parameter is the user request and the others are the fields of an account (cf. models.py, except unique and user).
    # Return False or the account added.

    # Creating the account
    new_acc = Account.objects.create(
        unique='.',
        name=normal_data(p_nam),
        type=acc_type_checker(p_typ),
        user=req.user,
        group=normal_data(p_grp),
        unit=normal_data(p_unt),
        gmt=int(p_gmt) if empty_checker(p_gmt) else 0,
        comment=normal_data(p_cmt)
    )
    return new_acc


def add_transaction(req: HttpRequest, dup: bool, p_acc, p_mkt, p_typ, p_dat, p_iin, p_out, p_ain, p_aou, p_prc, p_fee, p_feu, p_cmt):
    # Used to add a new transcation in the database.
    # The first parameter is the user request and the others are the fields of a transaction (cf. models.py).
    # Return False or the transaction added.

    # Getting the user account
    try:
        the_account = Account.objects.all().get(user__exact=req.user, unique__exact=p_acc)
    except Account.DoesNotExist:
        return False

    # Getting a possible duplicate transaction (account, date, input, output and amounts)
    try:
        old_tr = Transaction.objects.all().filter(
            account__exact=the_account,
            date__exact=date_checker(p_dat),
            input__exact=normal_data(p_iin),
            output__exact=normal_data(p_out),
            amountIn__exact=correct_number(p_ain),
            amountOut__exact=correct_number(p_aou)
        )[0]
    except IndexError:
        old_tr = False

    # If duplicate, update transaction
    if old_tr and dup:
        old_tr.market = normal_data(p_mkt)
        old_tr.type = tr_type_checker(p_typ)
        old_tr.price = correct_number(p_prc)
        old_tr.fee = correct_number(p_fee)
        old_tr.feeUnit = normal_data(p_feu)
        old_tr.comment = normal_data(p_cmt)
        old_tr.save()
        return old_tr

    # Else add the new transaction
    else:
        new_tf = Transaction.objects.create(
            account=the_account,
            market=normal_data(p_mkt),
            type=tr_type_checker(p_typ),
            date=date_checker(p_dat),
            input=normal_data(p_iin),
            output=normal_data(p_out),
            amountIn=correct_number(p_ain),
            amountOut=correct_number(p_aou),
            price=correct_number(p_prc),
            fee=correct_number(p_fee),
            feeUnit=normal_data(p_feu),
            comment=normal_data(p_cmt)
        )
        return new_tf


def add_transfer(req: HttpRequest, dup: bool, p_src, p_dst, p_dat, p_uni, p_amt, p_fee, p_feu, p_cmt):
    # Used to add a new transfer in the database.
    # The first parameter is the user request and the others are the fields of a transfer (cf. models.py).
    # Return False or the transfer added.

    # Getting the accounts
    try:
        the_source = Account.objects.all().get(unique__exact=p_src)
    except Account.DoesNotExist:
        return False
    try:
        the_destination = Account.objects.all().get(unique__exact=p_dst)
    except Account.DoesNotExist:
        return False

    # Verifying if one of the accounts belongs to the user
    if not the_source.user == req.user and not the_destination.user == req.user:
        return False

    # Getting a possible duplicate transfer (source, destination, date, unit, amount)
    try:
        old_tf = Transfer.objects.all().filter(
            source__exact=the_source,
            destination__exact=the_destination,
            date__exact=date_checker(p_dat),
            unit__exact=normal_data(p_uni),
            amount__exact=correct_number(p_amt)
        )[0]
    except IndexError:
        old_tf = False

    # If duplicate, update transfer
    if old_tf and dup:
        old_tf.fee = correct_number(p_fee)
        old_tf.feeUnit = normal_data(p_feu)
        old_tf.comment = normal_data(p_cmt)
        old_tf.save()
        return old_tf

    # Else add the new transfer
    else:
        new_tr = Transfer.objects.create(
            source=the_source,
            destination=the_destination,
            date=date_checker(p_dat),
            unit=normal_data(p_uni),
            amount=correct_number(p_amt),
            fee=correct_number(p_fee),
            feeUnit=normal_data(p_feu),
            comment=normal_data(p_cmt)
        )
        return new_tr


def mod_account(req: HttpRequest, p_nam, p_typ, p_grp, p_unt, p_gmt, p_cmt):
    # Used to modify an account in the database.
    # The first parameter is the user request and the others are the fields of an account (cf. models.py, except unique and user).
    # Return False or the account modified.

    # Getting the account
    try:
        the_acc = Account.objects.all().get(user__exact=req.user, name__exact=p_nam)
    except Account.DoesNotExist:
        return False

    # Modification of the account
    if empty_checker(p_typ):
        the_acc.type = "" if str(p_typ) == EMPTY else acc_type_checker(p_typ)
    if empty_checker(p_grp):
        the_acc.group = "" if str(p_grp) == EMPTY else normal_data(p_grp)
    if empty_checker(p_unt):
        the_acc.unit = "" if str(p_unt) == EMPTY else normal_data(p_unt)
    if empty_checker(p_gmt):
        the_acc.gmt = 0 if str(p_gmt) == EMPTY else int(p_gmt)
    if empty_checker(p_cmt):
        the_acc.comment = "" if str(p_cmt) == EMPTY else normal_data(p_cmt)
    the_acc.save()
    return the_acc


def mod_transaction(req: HttpRequest, p_id, p_mkt, p_typ, p_dat, p_iin, p_out, p_ain, p_aou, p_prc, p_fee, p_feu, p_cmt):
    # Used to modify a transcation in the database.
    # The first parameter is the user request, the second is the ID and the others are the fields of a transaction (cf. models.py, account excluded).
    # Return False or the transaction modified.

    # Getting the transaction
    try:
        the_tr = Transaction.objects.all().get(id__exact=p_id)
    except Transaction.DoesNotExist:
        return False

    # Verifying if the transaction belongs to the user
    try:
        Account.objects.all().get(user__exact=req.user, unique__exact=the_tr.account.unique)
    except Account.DoesNotExist:
        return False

    # Modification of the transaction
    if empty_checker(p_mkt):
        the_tr.market = "" if str(p_mkt) == EMPTY else normal_data(p_mkt)
    if empty_checker(p_typ):
        the_tr.type = "" if str(p_typ) == EMPTY else tr_type_checker(p_typ)
    if empty_checker(p_dat):
        the_tr.date = the_tr.date if str(p_dat) == EMPTY else date_checker(p_dat)
    if empty_checker(p_iin):
        the_tr.input = the_tr.input if str(p_iin) == EMPTY else normal_data(p_iin)
    if empty_checker(p_out):
        the_tr.output = the_tr.output if str(p_out) == EMPTY else normal_data(p_out)
    if empty_checker(p_ain):
        the_tr.amountIn = the_tr.amountIn if str(p_ain) == EMPTY else correct_number(p_ain)
    if empty_checker(p_aou):
        the_tr.amountOut = the_tr.amountOut if str(p_aou) == EMPTY else correct_number(p_aou)
    if empty_checker(p_prc):
        the_tr.price = 0 if str(p_prc) == EMPTY else correct_number(p_prc)
    if empty_checker(p_fee):
        the_tr.fee = 0 if str(p_fee) == EMPTY else correct_number(p_fee)
    if empty_checker(p_feu):
        the_tr.feeUnit = "" if str(p_feu) == EMPTY else normal_data(p_feu)
    if empty_checker(p_cmt):
        the_tr.comment = "" if str(p_cmt) == EMPTY else normal_data(p_cmt)
    the_tr.save()
    return the_tr


def mod_transfer(req: HttpRequest, p_id, p_src, p_dst, p_dat, p_uni, p_amt, p_fee, p_feu, p_cmt):
    # Used to modify a transfer in the database.
    # The first parameter is the user request, the second is the ID and the others are the fields of a transfer (cf. models.py, account excluded).
    # Return False or the transfer modified.

    # Getting the transfer
    try:
        the_tf = Transfer.objects.all().get(id__exact=p_id)
    except Transfer.DoesNotExist:
        return False

    # Getting the accounts
    try:
        the_source = Account.objects.all().get(unique__exact=the_tf.source.unique)
    except Account.DoesNotExist:
        return False
    try:
        the_destination = Account.objects.all().get(unique__exact=the_tf.destination.unique)
    except Account.DoesNotExist:
        return False

    # Verifying if one of the accounts belongs to the user
    if not the_source.user == req.user and not the_destination.user == req.user:
        return False

    # Verifying if with the news accounts one of them still belongs to the user
    if empty_checker(p_src):
        try:
            new_source = Account.objects.all().get(unique__exact=p_src)
        except Account.DoesNotExist:
            return False
    else:
        new_source = the_source

    if empty_checker(p_dst):
        try:
            new_destination = Account.objects.all().get(unique__exact=p_dst)
        except Account.DoesNotExist:
            return False
    else:
        new_destination = the_destination

    if not new_source.user == req.user and not new_destination.user == req.user:
        return False

    # Modification of the transfer
    if empty_checker(p_src):
        the_tf.source = the_tf.source if str(p_src) == EMPTY else new_source
    if empty_checker(p_dst):
        the_tf.destination = the_tf.destination if str(p_dst) == EMPTY else new_destination
    if empty_checker(p_dat):
        the_tf.date = the_tf.date if str(p_dat) == EMPTY else date_checker(p_dat)
    if empty_checker(p_uni):
        the_tf.unit = the_tf.unit if str(p_uni) == EMPTY else correct_number(p_uni)
    if empty_checker(p_amt):
        the_tf.amount = the_tf.amount if str(p_amt) == EMPTY else correct_number(p_amt)
    if empty_checker(p_fee):
        the_tf.fee = 0 if str(p_fee) == EMPTY else correct_number(p_fee)
    if empty_checker(p_feu):
        the_tf.feeUnit = "" if str(p_feu) == EMPTY else normal_data(p_feu)
    if empty_checker(p_cmt):
        the_tf.comment = "" if str(p_cmt) == EMPTY else normal_data(p_cmt)
    the_tf.save()
    return the_tf


def del_account(req: HttpRequest, p_nam):
    # Used to delete an account in the database.
    # The first parameter is the user request and the second is the name.
    # Return False or True.

    # Deleting the account
    Account.objects.all().filter(user__exact=req.user, name__exact=p_nam).delete()
    return True


def del_transaction(req: HttpRequest, p_id):
    # Used to delete a transcation in the database.
    # The first parameter is the user request and the second is the ID.
    # Return False or True.

    # Getting the transaction
    try:
        the_tr = Transaction.objects.all().get(id__exact=p_id)
    except Transaction.DoesNotExist:
        return False

    # Verifying if the transaction belongs to the user
    try:
        the_account = Account.objects.all().get(user__exact=req.user, unique__exact=the_tr.account.unique)
    except Account.DoesNotExist:
        return False

    # Deleting transaction
    Transaction.objects.all().filter(account__exact=the_account, id__exact=p_id).delete()
    return True


def del_transfer(req: HttpRequest, p_id):
    # Used to delete a transfer in the database.
    # The first parameter is the user request and the second is the ID.
    # Return False or True.

    # Getting the transfer
    try:
        the_tf = Transfer.objects.all().get(id__exact=p_id)
    except Transfer.DoesNotExist:
        return False

    # Getting the accounts
    try:
        the_source = Account.objects.all().get(unique__exact=the_tf.source.unique)
    except Account.DoesNotExist:
        return False
    try:
        the_destination = Account.objects.all().get(unique__exact=the_tf.destination.unique)
    except Account.DoesNotExist:
        return False

    # Verifying if one of the accounts belongs to the user
    if not the_source.user == req.user and not the_destination.user == req.user:
        return False

    # Deleting transfer
    Transfer.objects.all().filter(Q(id__exact=p_id), Q(source__exact=the_source) | Q(destination__exact=the_destination)).delete()
    return True


def empty_checker(data):
    # Verifiy if the variable is not empty
    if data is not None:
        if len(str(data)) > 0:
            return True
    return False


def acc_type_checker(atype):
    # Normalise the type for a transaction

    if Standard.objects.all().filter(type__exact='AccountType', name__exact=atype).exists():
        return atype
    return str("")


def tr_type_checker(atype):
    # Normalise the type for a transaction

    if Standard.objects.all().filter(type__exact='TransactionType', name__exact=atype).exists():
        return atype
    return str("")


def date_checker(date):
    # Normalise the date

    return parser.parse(date).isoformat()


def correct_number(number):
    # Normalise the number
    if empty_checker(number):
        return float(str(number).replace(",", ".").replace("-", ""))
    return 0


def normal_data(data):
    # Normalise basic data (not doing anything)

    return str(data)
