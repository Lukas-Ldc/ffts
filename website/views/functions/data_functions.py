"""
This is the data functions module.
"""
from decimal import Decimal
from re import sub as resub
from collections import Counter
from zoneinfo import ZoneInfo, available_timezones
from dateutil import parser
from django.db.models import Q
from django.utils.timezone import is_aware
from website.models import Transfer, Transaction, Account, Standard


def float_0_cleaner(number: float):
    """Clean any number given: '140.93000000'>'140.93', '140.0000'>'140'.

    Args:
        number (float): The number to clean

    Returns:
        float or int: The cleaned number
    """
    if number is not None:
        return number.quantize(Decimal(1)) if number == number.to_integral() else number.normalize()
    return None


def float_str_cleaner(number: str):
    """Removes any letter and comma from a string.

    Args:
        number (str): The string to clean

    Returns:
        float: The cleaned number
    """
    if number is not None and len(number) > 0:
        return float(resub(r'[A-Za-z,]', '', number))
    return None


def float_limiter(number: float, setting: int):
    """Depending on the size of the number, limits the number of digits after the decimal point

    Args:
        number (float): The number to clean
        setting (int): The limiter selected

    Returns:
        float: The cleaned number
    """
    if setting == 0:
        if number > 1000:
            return round(number, 1)
        if number > 100:
            return round(number, 2)
        if number > 10:
            return round(number, 3)
        if number > 1:
            return round(number, 4)
        return round(number, 8)

    if setting == 1:
        if number > 100:
            return round(number, 3)
        if number > 10:
            return round(number, 6)
        if number > 1:
            return round(number, 8)
        if number > 0.1:
            return round(number, 10)
        return round(number, 15)

    return None


def letter_only(data):
    """Return a string with all the numbers (and .&,) removed

    Args:
        data (str): The data to clean

    Returns:
        str: The data cleaned
    """
    if data is not None and len(data) > 0:
        return resub(r'[0-9,.]', '', data)
    return None


def strn(data, comma = ",", flot = False):
    """Return a string from anything or None if string empty.

    Args:
        data (any): The data to convert
        comma (str): Replace the comma by this value
        flot (bool): Return a float instead of a string

    Returns:
        str: The data converted to a string or None
    """
    if data is not None and len(str(data)) > 0:
        data = str(data).replace(",", comma)
        return float(data) if flot else str(data)
    return None


def opposite(num: float, rnd = None):
    """Gives back the opposite of a number.

    Args:
        num (float): The number to reverse
        rnd (int): The round for the value (auto via float_limiter by default)

    Returns:
        float: The result of the operation
    """
    if num != 0:
        return float_limiter(1 / abs(float(num)), 0) if rnd is None else round(1 / abs(float(num)), rnd)
    return float(0)


def all_acc_units(account: str):
    """Returns the list of all the existing units used in an account.

    Args:
        account (str): The unique ID of the account targeted

    Returns:
        list: The list of units
    """
    all_units = []
    transfers = Transfer.objects.all().filter(Q(source__exact=account) | Q(destination__exact=account))
    transactions = Transaction.objects.all().filter(account__exact=account)

    for transfer in transfers.values('unit').order_by('unit').distinct():
        all_units.append(transfer.get('unit'))
    for transaction in transactions.values('input').order_by('input').distinct():
        all_units.append(transaction.get('input'))
    for transaction in transactions.values('output').order_by('output').distinct():
        all_units.append(transaction.get('output'))
    return list(set(all_units))


def acc_type_checker(tyype: str):
    """Checks if an account type is valid

    Args:
        type (str): The type to set for the account

    Returns:
        str: The type if it exists or an empty string
    """
    if Standard.objects.all().filter(type__exact='AccountType', name__exact=tyype).exists():
        return tyype
    return None


def date_checker(date: str, utc: str, dayf: bool):
    """Transforms any date in a datetime object with the correct UTC

    Args:
        date (str): Any date to save
        utc (str): (1) Name of account: its UTC. (2) available_timezones from ZoneInfo: specific UTC. (!) If date is aware: date UTC prevails.
        dayf (bool): Day or month first (if True: 03 is day in 03-02-2020 or 2020-03-02)

    Returns:
        str: The ISO date
    """
    if date is None or len(date) == 0:
        return None
    date = parser.parse(date, dayfirst=dayf)

    # Date is aware of UTC or none given
    if utc is None or is_aware(date):
        return date
    # UTC is a time zone
    if utc in available_timezones():
        return date.replace(tzinfo=ZoneInfo(utc))
    # UTC is from an account
    if Account.objects.all().filter(unique__exact=utc):
        return date.replace(tzinfo=ZoneInfo(Account.objects.all().get(unique__exact=utc).utc))

    return date


def pair_spliter(pair: str, way: str, other_units: list = []):
    """Separates a pair (BTCUSDT) into two different tickers (BTC, USDT) by comparing with given data.

    Args:
        pair (str): The pair to split (BTCUSDT)
        way (str): BUY or SELL
        other_units (list): Other units that can help to split the pair (account units, fee units, ...)

    Returns:
        list: (INPUT, OUTPUT) or (PAIR, PAIR) if not guessed
    """
    unit1 = None

    # Trying to gess the unit
    for unit in other_units:
        if str(pair).startswith(unit):
            unit1 = unit
            break
        if str(pair).endswith(unit):
            unit1 = unit
            break

    # Unit guessed
    if unit1 is not None:
        unit2 = str(pair).replace(unit1, "")  # Removing unit guessed to get other unit

        if way == "BUY" and str(pair).startswith(unit1) or way == "SELL" and str(pair).startswith(unit2):
            return [unit2, unit1]
        elif way == "BUY" and str(pair).startswith(unit2) or way == "SELL" and str(pair).startswith(unit1):
            return [unit1, unit2]

    # Not guessed
    return [pair, pair]


def pair_guesser(account: str, unit: str):
    """Analyses all the transactions of an account to find the pair generally used with a specified unit.
    If an account unit is gaven, it will give another account unit in return (the one detected or the first in the account list).

    Args:
        account (str): Transactions from this account are used
        unit (str): The unit we want to guess the pair

    Returns:
        str: The guessed unit
    """
    account_units = Account.objects.all().get(unique__exact=account).unit

    opposites = []
    for transaction in Transaction.objects.all().filter(Q(account__exact=account) & Q(input__exact=unit) | Q(output__exact=unit)):
        if transaction.input == unit:
            opposites.append(transaction.output)
        else:
            opposites.append(transaction.input)

    if len(opposites) > 0:
        guess = Counter(opposites).most_common(1)[0][0]
        if unit in account_units and guess in account_units:
            return guess
        if unit not in account_units:
            return guess

    return account_units.split(",")[0]
