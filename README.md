# Free Finance Tracking Software
This web app helps you track easily your accounts. Add transactions, transfers and import data from any website using (or creating) an importation model. Internet connection is not used, and you can always export your data in CSV files. You can also have multiple users.

The login page:

<img src="/static/website/img/readme/ffts_login.png?raw=true" alt="The login page" width="800">

The accounts page:

<img src="/static/website/img/readme/ffts_accounts.png?raw=true" alt="The login page" width="800">

The account page:

<img src="/static/website/img/readme/ffts_account.png?raw=true" alt="The login page" width="800">

The transactions page:

<img src="/static/website/img/readme/ffts_transactions.png?raw=true" alt="The login page" width="800">

The transfers page:

<img src="/static/website/img/readme/ffts_transfers.png?raw=true" alt="The login page" width="800">

The importation page:

<img src="/static/website/img/readme/ffts_importation.png?raw=true" alt="The login page" width="800">

### How to install and use
You need to have <a href="https://www.python.org/" target="_blank">Python</a> and <a href="https://python-poetry.org/" target="_blank">Poetry</a> installed.

Install the environment and configure the server:
```
poetry install
poetry run python manage.py makemigrations
poetry run python manage.py migrate
poetry run python manage.py createsuperuser
```

Start the server:
```
poetry run python manage.py runserver
```
