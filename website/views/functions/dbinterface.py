"""
The is the database module.
Use the functions in this module to create, modify or delete accounts, transfers and transactions.
"""
from dateutil import parser
from django.db.models import Q
from django.http import HttpRequest
from website.models import Transaction, Transfer, Account, Standard

# Value used to clear a field during a modification
EMPTY = "0"


def add_account(request: HttpRequest, name: str, tyype: str, group: str, unit: str, gmt: int, comment: str):
    """Create a new account

    Args:
        request (HttpRequest): The HTTP request made to create the account
        name (str): The name of the account
        tyype (str): The type of the account
        group (str): The group of the account
        unit (str): The unit(s) of the account
        gmt (int): The GMT of the account
        comment (str): The cpmment of the account

    Returns:
        Account: The created account
    """
    new_acc = Account.objects.create(
        unique=None,
        name=normal_data(name),
        type=acc_type_checker(tyype),
        user=request.user,
        group=normal_data(group),
        unit=normal_data(unit),
        gmt=int(gmt) if empty_checker(gmt) else 0,
        comment=normal_data(comment)
    )
    return new_acc


def add_transaction(request: HttpRequest, antidup: bool, account: str, market: str, tyype: str, date: str, iinput: str, output: str, amount_in: str, amount_out: str, price: str, fee: str, fee_unit: str, comment: str):
    """Add a new transaction

    Args:
        request (HttpRequest): The HTTP request made to create the transaction
        antidup (bool): Check for duplicate in the database and update the existing if found
        account (str): The account which made the transaction
        market (str): The market
        tyype (str): The type
        date (str): The date
        iinput (str): The input
        output (str): The output
        amount_in (str): The amount of the input
        amount_out (str): The amount of the output
        price (str): The price
        fee (str): The fee
        fee_unit (str): The unit of the fee
        comment (str): The comment

    Returns:
        Transaction: False or the created transaction
    """
    # Getting the user account
    try:
        the_account = Account.objects.all().get(user__exact=request.user, unique__exact=account)
    except Account.DoesNotExist:
        return False

    # Getting a possible duplicate transaction (account, date, input, output and amounts: rows that make a transaction unique)
    try:
        old_tr = Transaction.objects.all().filter(
            account__exact=the_account,
            date__exact=date_checker(date),
            input__exact=normal_data(iinput),
            output__exact=normal_data(output),
            amountIn__exact=correct_number(amount_in),
            amountOut__exact=correct_number(amount_out)
        )[0]
    except IndexError:
        old_tr = False

    # If duplicate, update transaction (only the rows not used for unique detection)
    if old_tr and antidup:
        return mod_transaction(request, old_tr.id, market, tyype, str(old_tr.date), old_tr.input, old_tr.output, old_tr.amountIn, old_tr.amountOut, price, fee, fee_unit, comment)

    # Else add the new transaction
    else:
        new_tf = Transaction.objects.create(
            account=the_account,
            market=normal_data(market),
            type=normal_data(tyype),
            date=date_checker(date),
            input=normal_data(iinput),
            output=normal_data(output),
            amountIn=correct_number(amount_in),
            amountOut=correct_number(amount_out),
            price=correct_number(price),
            fee=correct_number(fee),
            feeUnit=normal_data(fee_unit),
            comment=normal_data(comment)
        )
        return new_tf


def add_transfer(request: HttpRequest, antidup: bool, source: str, destination: str, date: str, unit: str, amount: str, fee: str, fee_unit: str, comment: str):
    """Add a new transfer

    Args:
        request (HttpRequest): The HTTP request made to create the transfer
        antidup (bool): Check for duplicate in the database and update the existing if found
        source (str): The source
        destination (str): The destination
        date (str): The date
        unit (str): The unit
        amount (str): The amount
        fee (str): The fee
        fee_unit (str): The unit of the fee
        comment (str): The comment

    Returns:
        Transfer: False or the created transfer
    """
    # Getting the accounts
    try:
        the_source = Account.objects.all().get(unique__exact=source)
    except Account.DoesNotExist:
        return False
    try:
        the_destination = Account.objects.all().get(unique__exact=destination)
    except Account.DoesNotExist:
        return False

    # Verifying if one of the accounts belongs to the user
    if not the_source.user == request.user and not the_destination.user == request.user:
        return False

    # Getting a possible duplicate transfer (source, destination, date, unit, amount: rows that make a transfer unique)
    try:
        old_tf = Transfer.objects.all().filter(
            source__exact=the_source,
            destination__exact=the_destination,
            date__exact=date_checker(date),
            unit__exact=normal_data(unit),
            amount__exact=correct_number(amount)
        )[0]
    except IndexError:
        old_tf = False

    # If duplicate, update transfer (only the rows not used for unique detection)
    if old_tf and antidup:
        return mod_transfer(request, old_tf.id, old_tf.source, old_tf.destination, str(old_tf.date), old_tf.unit, old_tf.amount, fee, fee_unit, comment)

    # Else add the new transfer
    else:
        new_tr = Transfer.objects.create(
            source=the_source,
            destination=the_destination,
            date=date_checker(date),
            unit=normal_data(unit),
            amount=correct_number(amount),
            fee=correct_number(fee),
            feeUnit=normal_data(fee_unit),
            comment=normal_data(comment)
        )
        return new_tr


def mod_account(request: HttpRequest, name: str, tyype: str, group: str, unit: str, gmt: str, comment: str):
    """Modify an account

    Args:
        request (HttpRequest): The HTTP request made to modify the account
        name (str): The name of the account to modify
        tyype (str): The new type
        group (str): The new group
        unit (str): The new unit
        gmt (str): The new GMT
        comment (str): The new comment

    Returns:
        Account: False or the modified account
    """
    # Getting the account
    try:
        the_acc = Account.objects.all().get(user__exact=request.user, name__exact=name)
    except Account.DoesNotExist:
        return False

    # Modification of the account
    if empty_checker(tyype):
        the_acc.type = "" if str(tyype) == EMPTY else acc_type_checker(tyype)
    if empty_checker(group):
        the_acc.group = "" if str(group) == EMPTY else normal_data(group)
    if empty_checker(unit):
        the_acc.unit = "" if str(unit) == EMPTY else normal_data(unit)
    if empty_checker(gmt):
        the_acc.gmt = 0 if str(gmt) == EMPTY else int(gmt)
    if empty_checker(comment):
        the_acc.comment = "" if str(comment) == EMPTY else normal_data(comment)
    the_acc.save()
    return the_acc


def mod_transaction(request: HttpRequest, iid: int, market: str, tyype: str, date: str, iinput: str, output: str, amount_in: str, amount_out: str, price: str, fee: str, fee_unit: str, comment: str):
    """Modify a transaction

    Args:
        request (HttpRequest): The HTTP request made to modify the transaction
        iid (int): ID of the transaction to modify
        market (str): The new market
        tyype (str): The new type
        date (str): The new date
        iinput (str): The new input
        output (str): The new output
        amount_in (str): The new amount of the input
        amount_out (str): The new amount of the output
        price (str): The new price
        fee (str): The new fee
        fee_unit (str): The new unit of the fee
        comment (str): The new comment

    Returns:
        Transaction: False or the modified transaction
    """
    # Getting the transaction
    try:
        the_tr = Transaction.objects.all().get(id__exact=iid)
    except Transaction.DoesNotExist:
        return False

    # Verifying if the transaction belongs to the user
    try:
        Account.objects.all().get(user__exact=request.user, unique__exact=the_tr.account.unique)
    except Account.DoesNotExist:
        return False

    # Modification of the transaction
    if empty_checker(market):
        the_tr.market = "" if str(market) == EMPTY else normal_data(market)
    if empty_checker(tyype):
        the_tr.type = "" if str(tyype) == EMPTY else normal_data(tyype)
    if empty_checker(date):
        the_tr.date = the_tr.date if str(date) == EMPTY else date_checker(date)
    if empty_checker(iinput):
        the_tr.input = the_tr.input if str(iinput) == EMPTY else normal_data(iinput)
    if empty_checker(output):
        the_tr.output = the_tr.output if str(output) == EMPTY else normal_data(output)
    if empty_checker(amount_in):
        the_tr.amountIn = the_tr.amountIn if str(amount_in) == EMPTY else correct_number(amount_in)
    if empty_checker(amount_out):
        the_tr.amountOut = the_tr.amountOut if str(amount_out) == EMPTY else correct_number(amount_out)
    if empty_checker(price):
        the_tr.price = 0 if str(price) == EMPTY else correct_number(price)
    if empty_checker(fee):
        the_tr.fee = 0 if str(fee) == EMPTY else correct_number(fee)
    if empty_checker(fee_unit):
        the_tr.feeUnit = "" if str(fee_unit) == EMPTY else normal_data(fee_unit)
    if empty_checker(comment):
        the_tr.comment = "" if str(comment) == EMPTY else normal_data(comment)
    the_tr.save()
    return the_tr


def mod_transfer(request: HttpRequest, iid: int, source: str, destination: str, date: str, unit: str, amount: str, fee: str, fee_unit: str, comment: str):
    """Modify a transfer

    Args:
        request (HttpRequest): The HTTP request made to modify the transfer
        iid (int): The ID of the transfer to modify
        source (str): The new source
        destination (str): The new destination
        date (str): The new date
        unit (str): The new unit
        amount (str): The new amount
        fee (str): The new fee
        fee_unit (str): The new unit of the fee
        comment (str): The new comment

    Returns:
        Transfer: False or the modified transfer
    """
    # Getting the transfer
    try:
        the_tf = Transfer.objects.all().get(id__exact=iid)
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
    if not the_source.user == request.user and not the_destination.user == request.user:
        return False

    # Verifying if with the news accounts one of them still belongs to the user
    if empty_checker(source):
        try:
            new_source = Account.objects.all().get(unique__exact=source)
        except Account.DoesNotExist:
            return False
    else:
        new_source = the_source

    if empty_checker(destination):
        try:
            new_destination = Account.objects.all().get(unique__exact=destination)
        except Account.DoesNotExist:
            return False
    else:
        new_destination = the_destination

    if not new_source.user == request.user and not new_destination.user == request.user:
        return False

    # Modification of the transfer
    if empty_checker(source):
        the_tf.source = the_tf.source if str(source) == EMPTY else new_source
    if empty_checker(destination):
        the_tf.destination = the_tf.destination if str(destination) == EMPTY else new_destination
    if empty_checker(date):
        the_tf.date = the_tf.date if str(date) == EMPTY else date_checker(date)
    if empty_checker(unit):
        the_tf.unit = the_tf.unit if str(unit) == EMPTY else correct_number(unit)
    if empty_checker(amount):
        the_tf.amount = the_tf.amount if str(amount) == EMPTY else correct_number(amount)
    if empty_checker(fee):
        the_tf.fee = 0 if str(fee) == EMPTY else correct_number(fee)
    if empty_checker(fee_unit):
        the_tf.feeUnit = "" if str(fee_unit) == EMPTY else normal_data(fee_unit)
    if empty_checker(comment):
        the_tf.comment = "" if str(comment) == EMPTY else normal_data(comment)
    the_tf.save()
    return the_tf


def del_account(request: HttpRequest, name: str):
    """Delete an account

    Args:
        request (HttpRequest): The HTTP request made to delete the account
        name (str): The name of the account

    Returns:
        _bool_: True or error
    """
    # TODO: Verify if the account belong to the user before
    Account.objects.all().filter(user__exact=request.user, name__exact=name).delete()
    return True


def del_transaction(request: HttpRequest, iid: int):
    """Delete a transaction

    Args:
        request (HttpRequest): The HTTP request made to delete the transaction
        iid (int): The ID of the transaction

    Returns:
        bool: The transaction has been deleted or not
    """
    # Getting the transaction
    try:
        the_tr = Transaction.objects.all().get(id__exact=iid)
    except Transaction.DoesNotExist:
        return False

    # Verifying if the transaction belongs to the user
    try:
        the_account = Account.objects.all().get(user__exact=request.user, unique__exact=the_tr.account.unique)
    except Account.DoesNotExist:
        return False

    # Deleting transaction
    Transaction.objects.all().filter(account__exact=the_account, id__exact=iid).delete()
    return True


def del_transfer(request: HttpRequest, iid: int):
    """Delete a transfer

    Args:
        req (HttpRequest): The HTTP request made to delete the transfer
        iid (int): The ID of the transfer

    Returns:
        bool: The transfer has been deleted or not
    """
    # Getting the transfer
    try:
        the_tf = Transfer.objects.all().get(id__exact=iid)
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
    if not the_source.user == request.user and not the_destination.user == request.user:
        return False

    # Deleting transfer
    Transfer.objects.all().filter(Q(id__exact=iid), Q(source__exact=the_source) | Q(destination__exact=the_destination)).delete()
    return True


def empty_checker(string: str):
    """Verify if a string is empty

    Args:
        string (str): The string to check

    Returns:
        bool: True if not empty
    """
    # TODO: inverted, not instinctive
    if string is not None:
        if len(str(string)) > 0:
            return True
    return False


def acc_type_checker(tyype: str):
    """Checks if a type is valid for an account

    Args:
        type (str): The type to set for the account

    Returns:
        str: The type if it exists or an empty string
    """
    if Standard.objects.all().filter(type__exact='AccountType', name__exact=tyype).exists():
        return tyype
    return str("")


def date_checker(date: str):
    """Transforms any date in an ISO date

    Args:
        date (str): The non ISO date

    Returns:
        str: The ISO date
    """
    # FIXME: dayfirst:bool month or day first if parse confused
    return parser.parse(date).isoformat()


def correct_number(number: str):
    """Transforms a string in a number (removes '-' and replace ',' by '.')

    Args:
        number (str): The string to convert

    Returns:
        float: Returns the number or 0
    """
    if empty_checker(number):
        return float(str(number).replace(",", ".").replace("-", ""))
    return 0


def normal_data(data):
    """Return a string from anything

    Args:
        data (): The data to convert

    Returns:
        str: The data converted to a string
    """
    return str(data)
