from django.urls import path
from website.views import account, accounts, documentation, importation, login, logout, transactions, transfers

urlpatterns = [
    path('', accounts.accounts_view, name='website-accounts'),
    path('account/<name>', account.account_view, name='website-account'),
    path('accounts', accounts.accounts_view, name='website-accounts'),
    path('documentation', documentation.documentation_view, name='website-documentation'),
    path('importation/<account>', importation.importation_view, name='website-importation'),
    path('login', login.login_view, name='website-login'),
    path('logout', logout.logout_view, name='website-logout'),
    path('transactions/<account>', transactions.transactions_view, name='website-transactions'),
    path('transfers/<account>', transfers.transfers_view, name='website-transfers'),
]
