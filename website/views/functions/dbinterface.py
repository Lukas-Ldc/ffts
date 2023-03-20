"""
The is the database module.
Use the functions in this module to create, modify or delete accounts, transfers and transactions.
"""
from dateutil import parser
from zoneinfo import ZoneInfo
from django.db.models import Q
from django.http import HttpRequest
from django.utils.timezone import is_aware
from website.models import Transaction, Transfer, Account, Standard


def add_account(request: HttpRequest, name: str, tyype: str, group: str, unit: str, utc: str, comment: str):
    """Create a new account

    Args:
        request (HttpRequest): The HTTP request made to create the account
        name (str): The name of the account
        tyype (str): The type of the account
        group (str): The group of the account
        unit (str): The unit(s) of the account
        utc (str): The UTC of the account
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
        utc=normal_data(utc),
        comment=normal_data(comment)
    )
    return new_acc


def add_transaction(request: HttpRequest, antidup: bool, dayfirst: bool, account: str, market: str, tyype: str, date: str, iinput: str, output: str, amount_in: str, amount_out: str, price: str, fee: str, fee_unit: str, comment: str):
    """Add a new transaction

    Args:
        request (HttpRequest): The HTTP request made to create the transaction
        antidup (bool): Check for duplicate in the database and update the existing if found
        dayfirst (bool): In the date the day is before the month
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
            date__exact=date_checker(date, account, dayfirst),
            input__exact=normal_data(iinput),
            output__exact=normal_data(output),
            amount_in__exact=correct_number(amount_in),
            amount_out__exact=correct_number(amount_out)
        )[0]
    except IndexError:
        old_tr = False

    # If duplicate, update transaction (only the rows not used for unique detection)
    if old_tr and antidup:
        return mod_transaction(request, dayfirst, old_tr.id, market, tyype, str(old_tr.date), old_tr.input, old_tr.output, old_tr.amount_in, old_tr.amount_out, price, fee, fee_unit, comment)

    # Else add the new transaction
    else:
        new_tf = Transaction.objects.create(
            account=the_account,
            market=normal_data(market),
            type=normal_data(tyype),
            date=date_checker(date, account, dayfirst),
            input=normal_data(iinput),
            output=normal_data(output),
            amount_in=correct_number(amount_in),
            amount_out=correct_number(amount_out),
            price=correct_number(price),
            fee=correct_number(fee),
            feeUnit=normal_data(fee_unit),
            comment=normal_data(comment)
        )
        return new_tf


def add_transfer(request: HttpRequest, antidup: bool, dayfirst: bool, utc_acc: str, source: str, destination: str, date: str, unit: str, amount: str, fee: str, fee_unit: str, comment: str):
    """Add a new transfer

    Args:
        request (HttpRequest): The HTTP request made to create the transfer
        antidup (bool): Check for duplicate in the database and update the existing if found
        dayfirst (bool): In the date the day is before the month
        utc_acc (str): The account from which the UTC is used.
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
            date__exact=date_checker(date, utc_acc, dayfirst),
            unit__exact=normal_data(unit),
            amount__exact=correct_number(amount)
        )[0]
    except IndexError:
        old_tf = False

    # If duplicate, update transfer (only the rows not used for unique detection)
    if old_tf and antidup:
        return mod_transfer(request, dayfirst, utc_acc, old_tf.id, old_tf.source, old_tf.destination, str(old_tf.date), old_tf.unit, old_tf.amount, fee, fee_unit, comment)

    # Else add the new transfer
    else:
        new_tr = Transfer.objects.create(
            source=the_source,
            destination=the_destination,
            date=date_checker(date, utc_acc, dayfirst),
            unit=normal_data(unit),
            amount=correct_number(amount),
            fee=correct_number(fee),
            feeUnit=normal_data(fee_unit),
            comment=normal_data(comment)
        )
        return new_tr


def mod_account(request: HttpRequest, name: str, tyype: str, group: str, unit: str, utc: str, comment: str):
    """Modify an account

    Args:
        request (HttpRequest): The HTTP request made to modify the account
        name (str): The name of the account to modify
        tyype (str): The new type
        group (str): The new group
        unit (str): The new unit
        utc (str): The new UTC
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
    the_acc.type = empty_or_value(the_acc.type, acc_type_checker(tyype), True)
    the_acc.group = empty_or_value(the_acc.group, normal_data(group), True)
    the_acc.unit = empty_or_value(the_acc.unit, normal_data(unit), False)
    the_acc.utc = empty_or_value(the_acc.utc, normal_data(utc), False)
    the_acc.comment = empty_or_value(the_acc.comment, normal_data(comment), True)
    the_acc.save()
    return the_acc


def mod_transaction(request: HttpRequest, dayfirst: bool, iid: int, market: str, tyype: str, date: str, iinput: str, output: str, amount_in: str, amount_out: str, price: str, fee: str, fee_unit: str, comment: str):
    """Modify a transaction

    Args:
        request (HttpRequest): The HTTP request made to modify the transaction
        dayfirst (bool): In the date the day is before the month
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
    the_tr.market = empty_or_value(the_tr.market, normal_data(market), True)
    the_tr.type = empty_or_value(the_tr.type, normal_data(tyype), True)
    the_tr.date = empty_or_value(the_tr.date, date_checker(date, the_tr.account.unique, dayfirst), False)
    the_tr.input = empty_or_value(the_tr.input, normal_data(iinput), False)
    the_tr.output = empty_or_value(the_tr.output, normal_data(output), False)
    the_tr.amount_in = empty_or_value(the_tr.amount_in, correct_number(amount_in), False)
    the_tr.amount_out = empty_or_value(the_tr.amount_out, correct_number(amount_out), False)
    the_tr.price = empty_or_value(the_tr.price, correct_number(price), True)
    the_tr.fee = empty_or_value(the_tr.fee, correct_number(fee), True)
    the_tr.feeUnit = empty_or_value(the_tr.feeUnit, normal_data(fee_unit), True)
    the_tr.comment = empty_or_value(the_tr.comment, normal_data(comment), True)
    the_tr.save()
    return the_tr


def mod_transfer(request: HttpRequest, dayfirst: bool, utc_acc: str, iid: int, source: str, destination: str, date: str, unit: str, amount: str, fee: str, fee_unit: str, comment: str):
    """Modify a transfer

    Args:
        request (HttpRequest): The HTTP request made to modify the transfer
        dayfirst (bool): In the date the day is before the month
        utc_acc (str): The account from which the UTC is used.
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
    if not str_empty(source):
        try:
            new_source = Account.objects.all().get(unique__exact=source)
        except Account.DoesNotExist:
            return False
    else:
        new_source = the_source

    if not str_empty(destination):
        try:
            new_destination = Account.objects.all().get(unique__exact=destination)
        except Account.DoesNotExist:
            return False
    else:
        new_destination = the_destination

    if not new_source.user == request.user and not new_destination.user == request.user:
        return False

    # Modification of the transfer
    the_tf.source = empty_or_value(the_tf.source, new_source, False)
    the_tf.destination = empty_or_value(the_tf.destination, new_destination, False)
    the_tf.date = empty_or_value(the_tf.date, date_checker(date, utc_acc, dayfirst), False)
    the_tf.unit = empty_or_value(the_tf.unit, correct_number(unit), False)
    the_tf.amount = empty_or_value(the_tf.amount, correct_number(amount), False)
    the_tf.fee = empty_or_value(the_tf.fee, correct_number(fee), True)
    the_tf.feeUnit = empty_or_value(the_tf.feeUnit, normal_data(fee_unit), True)
    the_tf.comment = empty_or_value(the_tf.comment, normal_data(comment), True)
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
    try:
        account = Account.objects.all().get(user__exact=request.user, name__exact=name)
    except Account.DoesNotExist:
        return False
    account.delete()
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


def empty_or_value(old_value, new_value, can_none: bool):
    """Replaces an old value by a new value under certain conditions.

    Args:
        old_value (str, float, int): The value that might be replaced
        new_value (str, float, int): The new value
        can_none (bool): The old value can be empty (if new_value = "0") or not
    """
    if str(new_value) == "0" and isinstance(old_value, str):
        # "0" is the value cleaner for any string
        if can_none:
            old_value = ""
    else:
        if not str_empty(new_value):
            old_value = new_value
    return old_value


def str_empty(string: str):
    """Verify if a string is empty

    Args:
        string (str): The string to check

    Returns:
        bool: True if not empty
    """
    if string is not None:
        if len(str(string)) > 0:
            return False
    return True


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


def date_checker(date: str, account: str, dayf: bool = False):
    """Transforms any date in a datetime object

    Args:
        date (str): The non ISO date
        account(str): The account in which the data will be saved
        dayf (bool): Day or month first (if True: 03 is day in 03-02-2020 or 2020-03-02)

    Returns:
        str: The ISO date
    """
    if not str_empty(date):
        final_date = parser.parse(date, dayfirst=dayf)
        if not is_aware(final_date):
            timezone = ZoneInfo(Account.objects.all().get(unique__exact=account).utc)
            final_date = final_date.replace(tzinfo=timezone)
        return final_date
    return None


def correct_number(number: str):
    """Transforms a string in a number (absolute and replace ',' by '.')

    Args:
        number (str): The string to convert

    Returns:
        float: Returns the number or None
    """
    if not str_empty(number):
        return abs(float(str(number).replace(",", ".")))
    return None


def normal_data(data):
    """Return a string from anything

    Args:
        data (Any): The data to convert

    Returns:
        str: The data converted to a string or None
    """
    if not str_empty(data):
        return str(data)
    return None
