"""
This module defines the admin view.
"""
from django.contrib import admin
from .models import Account, Transfer, Transaction, Standard


class AccountInterface(admin.ModelAdmin):
    list_display = ['unique', 'name', 'type', 'user', 'group', 'unit', 'utc', 'comment']
    search_fields = ['name', 'group', 'unit', 'utc', 'comment']


class TransferInterface(admin.ModelAdmin):
    list_display = ['id', 'source', 'destination', 'date', 'unit', 'amount', 'fee', 'fee_unit', 'comment']
    search_fields = ['id', 'date', 'unit', 'fee_unit', 'comment']


class TransactionInterface(admin.ModelAdmin):
    list_display = ['id', 'account', 'market', 'type', 'date', 'input', 'output', 'amount_in', 'amount_out', 'price', 'fee', 'fee_unit', 'comment']
    search_fields = ['id', 'market', 'type', 'date', 'input', 'output', 'fee_unit', 'comment']


class StandardInterface(admin.ModelAdmin):
    list_display = ['type', 'name']
    search_fields = ['type', 'name']


admin.site.register(Account, AccountInterface)
admin.site.register(Transfer, TransferInterface)
admin.site.register(Transaction, TransactionInterface)
admin.site.register(Standard, StandardInterface)
