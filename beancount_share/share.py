"""
Plugin for Beancount to share expenses.

Credits: Based on Martin Blais <blais@furius.ca> personal snippet: https://github.com/beancount/beancount/issues/474.
"""
__author__ = "Akuukis"

from datetime import date, datetime
from typing import NamedTuple, Set, List, Union, Tuple
import re

from beancount.core.inventory import Inventory
from beancount.core.number import D, Decimal, ONE
from beancount.core.amount import Amount
from beancount.core.data import Account, Entries, Posting, Open, Transaction, new_metadata

from beancount_share.common import read_config, normalize_marked_txn, marked_postings, sum_income, sum_expenses, DIGITS_SET

__plugins__ = ('share',)


Config = NamedTuple(
    'Config', [
        ('mark', str),
        ('open_date', date),
        ('account_debtors', str),
        ('account_creditors', str),
        ('default_fraction', float),
        ('meta', dict),
        ('quantize', Decimal),
    ])


def share(entries: Entries, unused_options_map, config_string="{}") -> Entries:
    new_accounts: Set[Account] = set()
    new_entries: Entries = []

    # 1. Parse config
    config_obj = read_config(config_string)
    config = Config(
                           config_obj.pop('mark'              , 'share'),
        date.fromisoformat(config_obj.pop('open_date'         , '1970-01-01')),
                           config_obj.pop('account_debtors'   , 'Assets:Debtors'),
                           config_obj.pop('account_creditors' , 'Liabilities:Creditors'),
                     float(config_obj.pop('default_fraction'  , 0.5)),
                           config_obj.pop('meta'              , {}),
                     D(str(config_obj.pop('quantize'          , 0.01))),
    )

    for entry in entries:
        if not isinstance(entry, Transaction):
            new_entries.append(entry)
        else:
            # 2. Normalize marks.
            tx = normalize_marked_txn(entry, config.mark)

            # 3. Determine whenever this is debtor or creditor transactions.
            account_prefix: str
            total_income = sum_income(tx)
            total_expenses = sum_expenses(tx)
            total_value: Amount
            if(not total_expenses.is_empty() and total_income.is_empty()):
                account_prefix = config.account_debtors + ':'
                total_value = total_expenses.get_currency_units('EUR')
            elif(total_expenses.is_empty() and not total_income.is_empty()):
                account_prefix = config.account_creditors + ':'
                total_value = total_income.get_currency_units('EUR')
            else:
                raise Exception("Plugin \"share\" doesn't work on transactions that has both income and expense: please split it up into two transactions instead.")

            # 4. Per posting, split it up based on marks.
            new_postings = []
            for marks, posting in marked_postings(tx, config.mark, ("Income", "Expenses")):

                # 4.1. or skip if not marked.
                if(marks == None):
                    new_postings.append(posting)
                    continue

                # 5. Per mark, create a new posting.
                todo_absolute: List[Tuple[Amount, str]] = list()
                todo_percent: List[Tuple[float, str]] = list()
                todo_absent: List[str] = list()
                for mark in marks:
                    print(mark)
                    parts = mark.split('-')
                    account: str

                    # 5.1. Apply defaults.
                    try:
                        account = parts[0] if ':' in parts[0] else account_prefix + parts[0]
                        new_accounts.add(account)

                    except IndexError:
                        raise Exception("Mark \"{mark}\" must contain account name, e.g. \"#share-bob\".")

                    if(len(parts) > 1):
                        if('%' in parts[1] or 'p' in parts[1]):
                            try:
                                todo_percent.append((float(parts[1].split('%')[0].split('p')[0])/100, account))
                            except IndexError:
                                raise Exception("Something wrong with percent fraction {parts[1]}, please use a dot, e.g. \"33.3%\".")
                        else:
                            try:
                                todo_absolute.append((Amount(D(parts[1]).quantize(config.quantize), posting.units.currency), account))
                            except IndexError:
                                raise Exception("Something wrong with absolute fraction {parts[1]}, please use a dot, e.g. \"33.3%\".")
                    else:
                        todo_absent.append(account)

                # if(sanity_check_percent > 1):
                #     raise Exception("Your posting \"{posting}\" in transaction \"{tx}\" went above 100%.")

                # if(sanity_check_sum > total_value):
                #     raise Exception("Your posting \"{posting}\" in transaction \"{tx}\" went above total transaction amount.")

                new_postings_inner = []
                # 5.2. Handle absolute amounts first: mutate original posting's amount & create new postings.
                for amount, account in todo_absolute:
                    posting = posting._replace(
                        units=posting.units._replace(number=(posting.units.number - amount.number).quantize(config.quantize)),
                    )
                    key_name = "shared" + ('' if not ("shared" in posting.meta) else str(900 + len([k for k in posting.meta if k[0:len("shared")] == "shared" and set(k[len("shared"):]) <= DIGITS_SET])))
                    posting.meta[key_name] = account + " " + amount.to_string()
                    new_postings_inner.append(Posting(
                        account,
                        units=posting.units._replace(number=(amount.number).quantize(config.quantize)),
                        cost=posting.cost,
                        price=None,
                        flag=None,
                        meta=config.meta if config.meta else {"shared": posting.account + " " + amount.to_string()}
                    ))

                # 5.3. Handle relative amounts second: create new postings.
                remainder = posting.units
                total = D(0)
                for percent, account in todo_percent:
                    units = posting.units._replace(number=(D(float(remainder.number) * percent)).quantize(config.quantize))
                    total = total + units.number
                    new_postings_inner.append(Posting(
                        account,
                        units=units,
                        cost=posting.cost,
                        price=None,
                        flag=None,
                        meta=config.meta if config.meta else {"shared": posting.account + " " + str(int(percent * 100))+'% (' + units.to_string() + ')'}
                    ))
                    key_name = "shared" + ('' if not ("shared" in posting.meta) else str(900 + len([k for k in posting.meta if k[0:len("shared")] == "shared" and set(k[len("shared"):]) <= DIGITS_SET])))
                    posting.meta[key_name] = account + " " + str(int(percent * 100))+'% (' + units.to_string() + ')'

                # 5.4. Handle absent amounts third: create new postings.
                total_percent = sum(i for i, _ in todo_percent)
                percent = (1 - total_percent) / (1 + len(todo_absent))
                for account in todo_absent:
                    units = posting.units._replace(number=(D(float(remainder.number) * percent)).quantize(config.quantize))
                    total = total + units.number
                    new_postings_inner.append(Posting(
                        account,
                        units=units,
                        cost=posting.cost,
                        price=None,
                        flag=None,
                        meta=config.meta if config.meta else {"shared": posting.account + " (" + str(int(percent * 100))+'%, ' + units.to_string() + ')'}
                    ))
                    key_name = "shared" + ('' if not ("shared" in posting.meta) else str(900 + len([k for k in posting.meta if k[0:len("shared")] == "shared" and set(k[len("shared"):]) <= DIGITS_SET])))
                    posting.meta[key_name] = account + " (" + str(int(percent * 100))+'%, ' + units.to_string() + ')'

                # 5.5. Handle original posting last (mutate!).
                posting = posting._replace(
                    units=posting.units._replace(number=(remainder.number - total).quantize(config.quantize))
                )

                # if(posting.units.number > D(0)):
                new_postings.append(posting)

                new_postings.extend(new_postings_inner)

            for account in new_accounts:
                new_postings = group_postings(new_postings, account)

            new_entries.append(tx._replace(
                postings=new_postings,
            ))
            continue

        # deep else:

    for account in sorted(new_accounts):
        new_meta = new_metadata(entries[0].meta['filename'], 0)
        open_entry = Open(new_meta, config.open_date, account, None, None)
        new_entries.append(open_entry)

    return new_entries, []


def group_postings(postings: List[Posting], account: Account) -> List[Posting]:
    grouped_postings = []
    share_postings = []
    share_balance = Inventory()
    for posting in postings:
        if posting.account == account:
            share_postings.append(posting)
            share_balance.add_position(posting)
        else:
            grouped_postings.append(posting)
    if share_postings:
        for pos in share_balance:
            grouped_postings.append(
                Posting(account, pos.units, pos.cost, None, None, share_postings[0].meta))
    return grouped_postings
