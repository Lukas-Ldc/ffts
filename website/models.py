from django.db import models
from django.contrib.auth.models import User

class Account(models.Model):
    unique = models.CharField(max_length=200, primary_key=True)
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=50, null=True, blank=True)
    user = models.ForeignKey(User, to_field='username', on_delete=models.CASCADE)
    group = models.CharField(max_length=50, null=True, blank=True)
    unit = models.CharField(max_length=30, null=True, blank=True)
    gmt = models.DecimalField(max_digits=2, decimal_places=0, null=True, blank=True)
    comment = models.CharField(max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.unique = str(self.user) + '_' + str(self.name)
        super().save(*args, **kwargs)

class Transfer(models.Model):
    source = models.ForeignKey(Account, to_field='unique', on_delete=models.CASCADE, related_name='source_account')
    destination = models.ForeignKey(Account, to_field='unique', on_delete=models.CASCADE, related_name='destination_account')
    date = models.DateTimeField()
    unit = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=30, decimal_places=15)
    fee = models.DecimalField(max_digits=30, decimal_places=15, null=True, blank=True)
    feeType = models.CharField(max_length=15, null=True, blank=True)
    comment = models.CharField(max_length=255, null=True, blank=True)

class Transaction(models.Model):
    account = models.ForeignKey(Account, to_field='unique', on_delete=models.CASCADE)
    market = models.CharField(max_length=30, null=True, blank=True)
    type = models.CharField(max_length=30, null=True, blank=True)
    date = models.DateTimeField()
    input = models.CharField(max_length=15)
    output = models.CharField(max_length=15)
    amountIn = models.DecimalField(max_digits=30, decimal_places=15)
    amountOut = models.DecimalField(max_digits=30, decimal_places=15)
    price = models.DecimalField(max_digits=30, decimal_places=15, null=True, blank=True)
    fee = models.DecimalField(max_digits=30, decimal_places=15, null=True, blank=True)
    feeType = models.CharField(max_length=15, null=True, blank=True)
    comment = models.CharField(max_length=255, null=True, blank=True)

Standard_Types = [
    ('AccountType','AccountType'),
    ('TransactionType','TransactionType'),
    ('MyGMTtime','MyGMTtime'),
]

class Standard(models.Model):
    type = models.CharField(max_length=30, choices=Standard_Types)
    name = models.CharField(max_length=30)
