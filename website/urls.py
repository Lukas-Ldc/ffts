from django.urls import path
from website.views.account import account_view
from website.views.accounts import accounts_view
from website.views.documentation import documentation_view
from website.views.importation import importation_view
from website.views.login import login_view
from website.views.logout import logout_view
from website.views.transactions import transactions_view
from website.views.transfers import transfers_view

urlpatterns = [
    path('', accounts_view, name='website-accounts'),
    path('account/<name>', account_view, name='website-account'),
    path('accounts', accounts_view, name='website-accounts'),
    path('documentation', documentation_view, name='website-documentation'),
    path('importation/<account>', importation_view, name='website-importation'),
    path('login', login_view, name='website-login'),
    path('logout', logout_view, name='website-logout'),
    path('transactions/<account>', transactions_view, name='website-transactions'),
    path('transfers/<account>', transfers_view, name='website-transfers'),
]
