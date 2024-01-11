"""
The is the database module.
Use the functions in this module to create, modify or delete accounts, transfers and transactions.
"""
from datetime import datetime
from django.db.models import Q
from django.http import HttpRequest
from website.models import Transaction, Transfer, Account
from website.views.functions.data_functions import strn, date_checker, acc_type_checker


def add_account(request: HttpRequest, dayfirst: bool, name: str, tyype: str, group: str, unit: str, utc: str, open_d: str, close_d: str, comment: str):
    """Create a new account

    Args:
        request (HttpRequest): The HTTP request made to create the account
        dayfirst (bool): In the date the day is at the left of the month
        name (str): The name of the account
        tyype (str): The type of the account
        group (str): The group of the account
        unit (str): The unit(s) of the account
        utc (str): The UTC of the account
        open_d (str): The openning date of the account
        close_d (str): The closing date of the account
        comment (str): The cpmment of the account

    Returns:
        Account: The created account
    """
    new_acc = Account.objects.create(
        unique=None,
        name=strn(name),
        type=acc_type_checker(tyype),
        user=request.user,
        group=strn(group),
        unit=strn(unit),
        utc=strn(utc),
        open_date=date_checker(open_d, utc, dayfirst, True),
        close_date=date_checker(close_d, utc, dayfirst, True),
        comment=strn(comment)
    )
    return new_acc


def add_transaction(request: HttpRequest, antidup: bool, dayfirst: bool, utc: str, account: str, market: str, tyype: str, date: str, iinput: str, output: str, amount_in: str, amount_out: str, price: str, fee: str, fee_unit: str, comment: str, antidupcom: bool = False):
    """Add a new transaction

    Args:
        request (HttpRequest): The HTTP request made to create the transaction
        antidup (bool): Check for duplicate in the database and update the existing if found (account, date, in, out, amouts)
        dayfirst (bool): In the date the day is at the left of the month
        utc (str): Name of account: its UTC. available_timezones from ZoneInfo: specific UTC. If date is aware: date UTC prevails.
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
        antidupcom (bool): Also use the comment to check for duplicate

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
        if not antidupcom:
            old_tr = Transaction.objects.all().filter(
                account__exact=the_account,
                date__exact=date_checker(date, utc, dayfirst),
                input__exact=strn(iinput),
                output__exact=strn(output),
                amount_in__exact=abs(strn(amount_in, ".", True)),
                amount_out__exact=abs(strn(amount_out, ".", True))
            )[0]
        else:
            old_tr = Transaction.objects.all().filter(
                account__exact=the_account,
                date__exact=date_checker(date, utc, dayfirst),
                input__exact=strn(iinput),
                output__exact=strn(output),
                amount_in__exact=abs(strn(amount_in, ".", True)),
                amount_out__exact=abs(strn(amount_out, ".", True)),
                comment__exact=comment
            )[0]
    except IndexError:
        old_tr = False

    # If duplicate, update transaction (only the rows not used for unique detection)
    if old_tr and antidup:
        return mod_transaction(request, dayfirst, None, old_tr.id, market, tyype, None, None, None, None, None, price, fee, fee_unit, comment)

    # Else add the new transaction
    else:
        new_tf = Transaction.objects.create(
            account=the_account,
            market=strn(market),
            type=strn(tyype),
            date=date_checker(date, utc, dayfirst),
            input=strn(iinput),
            output=strn(output),
            amount_in=strn(amount_in, "."),
            amount_out=strn(amount_out, "."),
            price=strn(price, "."),
            fee=strn(fee, "."),
            fee_unit=strn(fee_unit),
            comment=strn(comment)
        )
        return new_tf


def add_transfer(request: HttpRequest, antidup: bool, dayfirst: bool, utc: str, source: str, destination: str, date: str, unit: str, amount: str, fee: str, fee_unit: str, comment: str, antidupcom: bool = False):
    """Add a new transfer

    Args:
        request (HttpRequest): The HTTP request made to create the transfer
        antidup (bool): Check for duplicate in the database and update the existing if found (source, dest, date, unit, amount)
        dayfirst (bool): In the date the day is at the left of the month
        utc (str): Name of account: its UTC. available_timezones from ZoneInfo: specific UTC. If date is aware: date UTC prevails.
        source (str): The source
        destination (str): The destination
        date (str): The date
        unit (str): The unit
        amount (str): The amount
        fee (str): The fee
        fee_unit (str): The unit of the fee
        comment (str): The comment
        antidupcom (bool): Also use the comment to check for duplicate

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
        if not antidupcom:
            old_tf = Transfer.objects.all().filter(
                source__exact=the_source,
                destination__exact=the_destination,
                date__exact=date_checker(date, utc, dayfirst),
                unit__exact=strn(unit),
                amount__exact=abs(strn(amount, ".", True))
            )[0]
        else:
            old_tf = Transfer.objects.all().filter(
                source__exact=the_source,
                destination__exact=the_destination,
                date__exact=date_checker(date, utc, dayfirst),
                unit__exact=strn(unit),
                amount__exact=abs(strn(amount, ".", True)),
                comment__exact=comment
            )[0]
    except IndexError:
        old_tf = False

    # If duplicate, update transfer (only the rows not used for unique detection)
    if old_tf and antidup:
        return mod_transfer(request, dayfirst, None, old_tf.id, old_tf.source, old_tf.destination, None, None, None, fee, fee_unit, comment)

    # Else add the new transfer
    else:
        new_tr = Transfer.objects.create(
            source=the_source,
            destination=the_destination,
            date=date_checker(date, utc, dayfirst),
            unit=strn(unit),
            amount=strn(amount, "."),
            fee=strn(fee, "."),
            fee_unit=strn(fee_unit),
            comment=strn(comment)
        )
        return new_tr


def mod_account(request: HttpRequest, dayfirst: bool, name: str, tyype: str, group: str, unit: str, utc: str, open_d: str, close_d: str, comment: str):
    """Modify an account

    Args:
        request (HttpRequest): The HTTP request made to modify the account
        dayfirst (bool): In the date the day is at the left of the month
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
    the_acc.group = empty_or_value(the_acc.group, strn(group), True)
    the_acc.unit = empty_or_value(the_acc.unit, strn(unit), False)
    the_acc.utc = empty_or_value(the_acc.utc, strn(utc), False)
    the_acc.open_date = empty_or_value(the_acc.open_date, date_checker(open_d, utc, dayfirst, True), True)
    the_acc.close_date = empty_or_value(the_acc.close_date, date_checker(close_d, utc, dayfirst, True), True)
    the_acc.comment = empty_or_value(the_acc.comment, strn(comment), True)
    the_acc.save()
    return the_acc


def mod_transaction(request: HttpRequest, dayfirst: bool, utc: str, iid: int, market: str, tyype: str, date: str, iinput: str, output: str, amount_in: str, amount_out: str, price: str, fee: str, fee_unit: str, comment: str):
    """Modify a transaction

    Args:
        request (HttpRequest): The HTTP request made to modify the transaction
        dayfirst (bool): In the date the day is at the left of the month
        utc (str): NName of account: its UTC. available_timezones from ZoneInfo: specific UTC. If date is aware: date UTC prevails.
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
    the_tr.market = empty_or_value(the_tr.market, strn(market), True)
    the_tr.type = empty_or_value(the_tr.type, strn(tyype), True)
    the_tr.date = empty_or_value(the_tr.date, date_checker(date, utc, dayfirst), False)
    the_tr.input = empty_or_value(the_tr.input, strn(iinput), False)
    the_tr.output = empty_or_value(the_tr.output, strn(output), False)
    the_tr.amount_in = empty_or_value(the_tr.amount_in, strn(amount_in, ".", True), False)
    the_tr.amount_out = empty_or_value(the_tr.amount_out, strn(amount_out, ".", True), False)
    the_tr.price = empty_or_value(the_tr.price, strn(price, ".", True), False)
    the_tr.fee = empty_or_value(the_tr.fee, strn(fee, ".", True), True)
    the_tr.fee_unit = empty_or_value(the_tr.fee_unit, strn(fee_unit), True)
    the_tr.comment = empty_or_value(the_tr.comment, strn(comment), True)
    the_tr.save()
    return the_tr


def mod_transfer(request: HttpRequest, dayfirst: bool, utc: str, iid: int, source: str, destination: str, date: str, unit: str, amount: str, fee: str, fee_unit: str, comment: str):
    """Modify a transfer

    Args:
        request (HttpRequest): The HTTP request made to modify the transfer
        dayfirst (bool): In the date the day is at the left of the month
        utc (str): Name of account: its UTC. available_timezones from ZoneInfo: specific UTC. If date is aware: date UTC prevails.
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
    if source is not None and len(str(source)) > 0:
        try:
            new_source = Account.objects.all().get(unique__exact=source)
        except Account.DoesNotExist:
            return False
    else:
        new_source = the_source

    if destination is not None and len(str(destination)) > 0:
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
    the_tf.date = empty_or_value(the_tf.date, date_checker(date, utc, dayfirst), False)
    the_tf.unit = empty_or_value(the_tf.unit, strn(unit, ".", True), False)
    the_tf.amount = empty_or_value(the_tf.amount, strn(amount, ".", True), False)
    the_tf.fee = empty_or_value(the_tf.fee, strn(fee, ".", True), True)
    the_tf.fee_unit = empty_or_value(the_tf.fee_unit, strn(fee_unit), True)
    the_tf.comment = empty_or_value(the_tf.comment, strn(comment), True)
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
    """Replaces an old value by a new value under certains conditions.

    Args:
        old_value: The value that might be replaced
        new_value: The new value
        can_none (bool): The old value can be empty (if new_value = "0") or not
    """
    if can_none:
        if str(new_value) == "0" and isinstance(old_value, str):
            return None  # "0" is the value cleaner for a string
        elif isinstance(new_value, datetime) and new_value.year == 1:
            return None  # Year = 0001 is the value cleaner for a date

    if new_value is not None and len(str(new_value)) > 0:
        return new_value
    return old_value
