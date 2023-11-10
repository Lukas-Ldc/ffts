from io import StringIO
from copy import deepcopy
from csv import reader as csvreader
from bs4 import BeautifulSoup
from website.models import Account
from website.views.functions.data_functions import float_limiter, float_str_cleaner, all_acc_units, pair_spliter, pair_guesser, letter_only
from website.views.functions.dbinterface import add_transaction, add_transfer


def binance_importer(file, table: str, tr_type: str, transf_acc: str, acc: str, request, utc: str):
    """Import a binance export

    Args:
        file (file): The file that contains the data to import
        table (str): The type of data imported
        tr_type (str): The type of transaction
        transf_acc (str): The account linked to the withdrawals & deposits
        acc (str): The account that will receive the imported data
        request (HttpRequest): The request made to send the file
        utc (str): The timezone of the data from the imported file
    """

    if file.name.endswith('.csv'):

        # The user wants to import transactions
        if table == "Transactions":

            for column in csvreader(StringIO(file.read().decode('UTF-8')), delimiter=','):
                acc_unit = all_acc_units(acc)

                if len(column) == 8 and not column[0].startswith("Date"):
                    add_transaction(
                        request,
                        True,
                        False,
                        utc,
                        acc,
                        "",
                        tr_type,
                        column[0],
                        pair_spliter(column[1], column[2], acc_unit.extend(column[7]))[0],
                        pair_spliter(column[1], column[2], acc_unit.extend(column[7]))[1],
                        float_str_cleaner(column[5]) if column[2] == "BUY" else float_str_cleaner(column[4]),
                        float_str_cleaner(column[4]) if column[2] == "BUY" else float_str_cleaner(column[5]),
                        float_str_cleaner(column[3]),
                        float_str_cleaner(column[6]),
                        column[7],
                        ""
                    )

                elif len(column) == 7 and not column[0].startswith("Date"):
                    acc_unit.append(letter_only(column[4]))
                    acc_unit.append(letter_only(column[5]))
                    acc_unit.append(letter_only(column[6]))

                    add_transaction(
                        request,
                        True,
                        False,
                        utc,
                        acc,
                        "",
                        tr_type,
                        column[0],
                        pair_spliter(column[1], column[2], acc_unit)[0],
                        pair_spliter(column[1], column[2], acc_unit)[1],
                        float_str_cleaner(column[5]) if column[2] == "BUY" else float_str_cleaner(column[4]),
                        float_str_cleaner(column[4]) if column[2] == "BUY" else float_str_cleaner(column[5]),
                        str(column[3]),
                        float_str_cleaner(column[6]),
                        letter_only(column[6]),
                        ""
                    )

        # The user wants to import crypto deposits or withdrawals
        elif table == "CryptoDeposit" or table == "CryptoWithdrawal":
            for column in csvreader(StringIO(file.read().decode('UTF-8')), delimiter=','):

                if len(column) > 0 and not column[0].startswith("Date"):
                    add_transfer(
                        request,
                        True,
                        False,
                        utc,
                        acc_gaver(table, "s", transf_acc, column[5], acc),
                        acc_gaver(table, "d", transf_acc, column[5], acc),
                        column[0],
                        column[1],
                        float_str_cleaner(column[3]),
                        float_str_cleaner(column[4]),
                        column[1],
                        "Via " + column[2]
                    )

        # The user wants to import fiat deposits or withdrawals
        elif table == "FiatDeposit" or table == "FiatWithdrawal":
            for column in csvreader(StringIO(file.read().decode('UTF-8')), delimiter=','):

                if len(column) > 0 and not column[0].startswith("Date"):
                    if column[3] == "Successful":
                        add_transfer(
                            request,
                            True,
                            False,
                            utc,
                            acc_gaver(table, "s", transf_acc, "", acc),
                            acc_gaver(table, "d", transf_acc, "", acc),
                            column[0],
                            column[1],
                            float_str_cleaner(column[2]),
                            float_str_cleaner(column[6]),
                            column[1],
                            column[4]
                        )

        # The user wants to import direct buy/sell : transfer (fiat) + transaction (crypto)
        elif table == "CryptoBuyDeposit":
            for column in csvreader(StringIO(file.read().decode('UTF-8')), delimiter=','):

                if len(column) > 0 and not column[0].startswith("Date"):
                    if column[6] == "Completed":
                        add_transfer(
                            request,
                            True,
                            False,
                            utc,
                            acc_gaver(table, "s", transf_acc, "", acc),
                            acc_gaver(table, "d", transf_acc, "", acc),
                            column[0],
                            column[2].split(" ")[1],
                            float_str_cleaner(column[2].split(" ")[0]) - float_str_cleaner(column[4].split(" ")[0]),
                            float_str_cleaner(column[4].split(" ")[0]),
                            column[4].split(" ")[1],
                            "Crypto Buy"
                        )
                        add_transaction(
                            request,
                            True,
                            False,
                            utc,
                            acc,
                            None,
                            tr_type,
                            column[0],
                            column[2].split(" ")[1],
                            column[5].split(" ")[1],
                            float_str_cleaner(column[2]) - float_str_cleaner(column[4]),
                            column[5].split(" ")[0],
                            None,
                            None,
                            None,
                            "Crypto Buy"
                        )

        elif table == "C2C":
            for column in csvreader(StringIO(file.read().decode('UTF-8')), delimiter=','):
                if column[3] == "C2C Transfer":
                    add_transfer(
                        request,
                        True,
                        False,
                        utc,
                        transf_acc if float_str_cleaner(column[5]) > 0  else acc,
                        acc if float_str_cleaner(column[5]) > 0  else transf_acc,
                        column[1],
                        column[4],
                        float_str_cleaner(column[5]),
                        0,
                        "",
                        "C2C"
                    )

        # The user wants to import interests & dust
        elif table == "Other" or table == "OtherBnb":
            file_base = deepcopy(file)  # Making a copy to be able to read in parallel if PoS
            stacked_in = ["Simple Earn Locked Subscription", "POS savings purchase", "Staking Purchase"]
            stacked_out = ["Simple Earn Locked Redemption", "POS savings redemption", "Staking Redemption", "Simple Earn Flexible Redemption"]
            stacked_interest = ["Simple Earn Locked Rewards", "POS savings interest", "Staking Rewards"]
            simple_interests = ["Distribution", "Simple Earn Flexible Interest", "Savings Interest", "Commission Rebate", "Cashback Voucher", "Airdrop Assets", "Asset Recovery"]

            for column in csvreader(StringIO(file.read().decode('UTF-8')), delimiter=','):
                if len(column) > 0 and not column[0].startswith("User_ID"):

                    # Simple interest (cancel anytime, what you've earned is earned) or distribution
                    if column[3] in simple_interests:
                        if not (len(column[4]) > 3 and str(column[4]).startswith('LD')):
                            add_transaction(
                                request,
                                True,
                                False,
                                utc,
                                acc,
                                "",
                                tr_type,
                                column[1],
                                pair_guesser(acc, column[4]) if column[3] != "Asset Recovery" else column[4],
                                column[4],
                                0 if column[3] != "Asset Recovery" else column[5],
                                column[5] if column[3] != "Asset Recovery" else 0,
                                0,
                                0,
                                "",
                                column[3]
                            )

                    # Dust (not the best way: output and input separated in 2 transactions)
                    elif column[3] == "Small Assets Exchange BNB" and table == "OtherBnb":
                        add_transaction(
                            request,
                            True,
                            False,
                            utc,
                            acc,
                            "",
                            tr_type,
                            column[1],
                            "#DUST#" if column[4] == "BNB" else column[4],
                            "BNB",
                            0 if column[4] == "BNB" else abs(float(column[5])),
                            abs(float(column[5])) if column[4] == "BNB" else 0,
                            0,
                            0,
                            "",
                            "SAE BNB"
                        )

                    # Locked interest (if you cancel, you wont earn the past interest)
                    # If 2 subscriptions for the same asset overlap + one of them is canceled : wrong numbers saved
                    elif column[3] in stacked_in:
                        filte_temp = deepcopy(file_base)  # New copy for each subscription to start to read from the begining
                        purchase_found = False  # The subscription has been found in the new copy
                        pos_interest = []  # The interest during the subscription
                        pos_purchase = 0  # The amount of the subscription
                        purchase_count = 0  # The number of purchase of the same asset (that overlap) : will add them all, so if one is cancelled it will be added too in the transactions
                        overlap = False  # At least two purchase for the same asset for locked subscription

                        for col in csvreader(StringIO(filte_temp.read().decode('UTF-8')), delimiter=','):

                            # If subscription found and interest from the subscription asset
                            if col[4] == column[4] and purchase_found and col[3] in stacked_interest:
                                temp = []
                                for ccol in [col[1], col[5]]:
                                    temp.append(ccol)
                                pos_interest.append(temp)

                            # Trying to find the subscription
                            elif col[3] in stacked_in and col[4] == column[4]:
                                if col[1] == column[1]:
                                    purchase_found = True
                                    pos_purchase = abs(float_str_cleaner(col[5]))
                                if purchase_found:
                                    purchase_count += 1
                                    if purchase_count > 1:
                                        overlap = True

                            # Redemption has been found
                            elif col[4] == column[4] and col[3] in stacked_out and purchase_found:
                                purchase_count -= 1
                                # If purchase from the same asset overlap, add them all or the ones after a redemption will never be added
                                if purchase_count == 0:
                                    # If not canceled (redemption amount >= purchase amount) or if same asset stacked overlap (no way to know if cancelled)
                                    if abs(float(col[5])) >= pos_purchase or overlap:
                                        # Saving transactions (2 subscritpions overlap not a problem: anti-duplicate protection)
                                        for i in pos_interest:
                                            add_transaction(
                                                request,
                                                True,
                                                False,
                                                utc,
                                                acc,
                                                "",
                                                tr_type,
                                                i[0],
                                                pair_guesser(acc, col[4]),
                                                col[4],
                                                0,
                                                abs(float(i[1])),
                                                0,
                                                0,
                                                "",
                                                "Locked Subscription"
                                            )
                                    break

    elif file.name.endswith('.html'):

        # The user wants to import dust
        if table == "BnbHtml":
            html_sae = BeautifulSoup(file, 'html.parser').find_all(class_="css-g9v9ex")[0]
            for sae_group in html_sae.find_all(class_="css-g9v9ex"):
                for sae in sae_group.find_all(class_="css-1f50q6c"):
                    sae = sae.find_all(class_=True)
                    try:
                        add_transaction(
                                request,
                                True,
                                False,
                                utc,
                                acc,
                                "",
                                tr_type,
                                sae[0].get_text(strip=True),
                                sae[1].get_text(strip=True),
                                "BNB",
                                sae[2].get_text(strip=True),
                                sae[4].get_text(strip=True),
                                None,
                                sae[3].get_text(strip=True),
                                "BNB",
                                "SAE"
                            )
                    except KeyError:
                        pass


def acc_gaver(table: str, direction: str, acc_linked: str, manual_val: str, account: str):
    """Gives one of the accounts for a transfer depending on different settings.

    Args:
        table (str): The table selected for the import (ends with Withdrawal or Deposit)
        direction (str): You need the source account ("s") or the destination ("d")
        acc_linked (str): Manual or the selected account (set in the HTML form)
        manual_val (str): If acc_linked=Manual: use this account (from the CSV)
        account (str): The account in which the data is imported

    Returns:
        Account: The account needed
    """
    # Source needed for a deposit / Destination needed for a withdrawal
    if (table.endswith("Deposit") and direction == "s") or (table.endswith("Withdrawal") and direction == "d"):
        if acc_linked == "Manual":
            return Account.objects.all().get(unique__exact=manual_val).unique
        else:
            return Account.objects.all().get(unique__exact=acc_linked).unique

    # Destination needed for a deposit / Source needed for a withdrawal
    elif (table.endswith("Deposit") and direction == "d") or (table.endswith("Withdrawal") and direction == "s"):
        return Account.objects.all().get(unique__exact=account).unique
