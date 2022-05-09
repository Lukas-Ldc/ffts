from django.contrib import admin
from .models import *

class Account_Interface(admin.ModelAdmin):
    list_display = ['unique', 'name', 'type', 'user', 'group', 'unit', 'comment']
    search_fields = ['unqiue', 'name', 'type', 'user', 'group', 'unit', 'comment']

class Transfer_Interface(admin.ModelAdmin):
    list_display = ['source','destination','date','unit','amount','fee','feeType','comment']
    search_fields = ['source','destination','date','unit','comment']

class Transaction_Interface(admin.ModelAdmin):
    list_display = ['account','market','type','date','input','output','amountIn','amountOut','multiplier','fee','feeType','comment']
    search_fields = ['account','market','type','date','input','output','comment']

admin.site.register(Account, Account_Interface)
admin.site.register(Transfer, Transfer_Interface)
admin.site.register(Transaction, Transaction_Interface)