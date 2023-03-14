"""
This module defines the admin view.
"""
from django.contrib import admin
from .models import Account, Transfer, Transaction, Standard


class AccountInterface(admin.ModelAdmin):
    list_display = ['unique', 'name', 'type', 'user', 'group', 'unit', 'utc', 'comment']
    search_fields = ['unqiue', 'name', 'type', 'user', 'group', 'unit', 'utc', 'comment']


class TransferInterface(admin.ModelAdmin):
    list_display = ['id', 'source', 'destination', 'date', 'unit', 'amount', 'fee', 'feeUnit', 'comment']
    search_fields = ['id', 'source', 'destination', 'date', 'unit', 'comment']


class TransactionInterface(admin.ModelAdmin):
    list_display = ['id', 'account', 'market', 'type', 'date', 'input', 'output', 'amount_in', 'amount_out', 'price', 'fee', 'feeUnit', 'comment']
    search_fields = ['id', 'account', 'market', 'type', 'date', 'input', 'output', 'comment']


class StandardInterface(admin.ModelAdmin):
    list_display = ['type', 'name']
    search_fields = ['type', 'name']


admin.site.register(Account, AccountInterface)
admin.site.register(Transfer, TransferInterface)
admin.site.register(Transaction, TransactionInterface)
admin.site.register(Standard, StandardInterface)
