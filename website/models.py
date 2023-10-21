"""
This module defines the database model.
"""
from zoneinfo import available_timezones
from django.db import models
from django.contrib.auth.models import User

Standard_Types = [
    ('AccountType', 'AccountType'),
    ('TransactionType', 'TransactionType')
]
TimeZones = [(tz, tz) for tz in sorted(available_timezones())]


class Account(models.Model):
    unique = models.CharField(max_length=200, primary_key=True)
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=50, null=True, blank=True)
    user = models.ForeignKey(User, to_field='username', on_delete=models.CASCADE)
    group = models.CharField(max_length=50, null=True, blank=True)
    unit = models.CharField(max_length=50)
    utc = models.CharField(max_length=50, choices=TimeZones)
    open_date = models.DateField(null=True, blank=True)
    close_date = models.DateField(null=True, blank=True)
    comment = models.CharField(max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.unique = str(self.user) + '_' + str(self.name)
        if self.utc not in available_timezones():
            raise ValueError("Account UTC is not valid.")
        super().save(*args, **kwargs)


class Transfer(models.Model):
    source = models.ForeignKey(Account, to_field='unique', on_delete=models.CASCADE, related_name='source_account')
    destination = models.ForeignKey(Account, to_field='unique', on_delete=models.CASCADE, related_name='destination_account')
    date = models.DateTimeField()
    unit = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=30, decimal_places=15)
    fee = models.DecimalField(max_digits=30, decimal_places=15, default=0)
    fee_unit = models.CharField(max_length=15, null=True, blank=True)
    comment = models.CharField(max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.amount = abs(float(self.amount))
        if self.fee is None:
            self.fee = 0
        else:
            self.fee = abs(float(self.fee))
        super().save(*args, **kwargs)


class Transaction(models.Model):
    account = models.ForeignKey(Account, to_field='unique', on_delete=models.CASCADE)
    market = models.CharField(max_length=30, null=True, blank=True)
    type = models.CharField(max_length=30, null=True, blank=True)
    date = models.DateTimeField()
    input = models.CharField(max_length=15)
    output = models.CharField(max_length=15)
    amount_in = models.DecimalField(max_digits=30, decimal_places=15)
    amount_out = models.DecimalField(max_digits=30, decimal_places=15)
    price = models.DecimalField(max_digits=30, decimal_places=15)
    fee = models.DecimalField(max_digits=30, decimal_places=15, default=0)
    fee_unit = models.CharField(max_length=15, null=True, blank=True)
    comment = models.CharField(max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.amount_in = abs(float(self.amount_in))
        self.amount_out = abs(float(self.amount_out))
        if self.price is None:
            if self.amount_out != 0:
                self.price = float_limiter(float(self.amount_in) / float(self.amount_out))
            else:
                self.price = 0
        else:
            self.price = abs(float(self.price))
        if self.fee is None:
            self.fee = 0
        else:
            self.fee = abs(float(self.fee))
        super().save(*args, **kwargs)


class Standard(models.Model):
    type = models.CharField(max_length=30, choices=Standard_Types)
    name = models.CharField(max_length=30)


def float_limiter(number: float):
    """Depending on the size of the number, limits the number of digits after the decimal point

    Args:
        number (float): The number to clean

    Returns:
        float: The cleaned number
    """
    if number > 1000:
        return round(number, 1)
    if number > 100:
        return round(number, 2)
    if number > 10:
        return round(number, 3)
    if number > 1:
        return round(number, 4)
    return round(number, 8)
