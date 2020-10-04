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
from beancount.core.data import Account, Entries, Posting, Open, Transaction, new_metadata

from beancount_share.common import read_config, normalized_marked_txns, marked_postings

__plugins__ = ('share',)


Config = NamedTuple(
    'Config', [
        ('mark', str),
        ('open_date', date),
        ('account_debtors', str),
        ('account_creditors', str),
        ('default_fraction', Decimal),
        ('meta', dict),
        ('quantize', Decimal),
    ])


def share(entries: Entries, unused_options_map, config_string="{}") -> Entries:
    new_accounts: Set[Account] = set()
    new_entries: Entries = []

    config_obj = read_config(config_string)
    config = Config(
                           config_obj.pop('mark'              , 'share'),
        date.fromisoformat(config_obj.pop('open_date'         , '1970-01-01')),
                           config_obj.pop('account_debtors'   , 'Assets:Debtors'),
                           config_obj.pop('account_creditors' , 'Liabilities:Creditors'),
                     D(str(config_obj.pop('default_fraction'  , 0.5))),
                           config_obj.pop('meta'              , {}),
                     D(str(config_obj.pop('quantize'          , 0.01))),
    )

    for entry in entries:
        if isinstance(entry, Transaction):
            for tx in normalized_marked_txns(entry, config.mark):
                new_postings = []
                for marks, posting in marked_postings(tx, config.mark):
                    if(marks == None):
                        new_postings.append(posting)
                        continue

                    names_and_fractions: List[Tuple[str, Union[Decimal, float]]] = list()
                    for mark in marks:
                        parts = mark.split('-')
                        account_name: str
                        fraction: Union[Decimal, float]
                        try:
                            account_name = parts[0]
                        except IndexError:
                            raise Exception("Mark \"{mark}\" must contain account name, e.g. \"#share-bob\".")
                        if('%' in parts[1]):
                            try:
                                fraction = float(parts[1].split('%')[0])
                            except IndexError:
                                raise Exception("Something wrong with percent fraction {parts[1]}, please use a dot, e.g. \"33.3%\".")
                        else:
                            try:
                                fraction = D(str(parts[1]))
                            except IndexError:
                                fraction = config.default_fraction
                        names_and_fractions.append((account_name, fraction))

                total_income = sum_income(entry)
                total_expense = sum_expense(entry)
                if(total_income > 0 and total_expense == 0):
                    account = config.account_debtors + ':' + account_name
                elif(total_income > 0 and total_expense == 0):
                    account = config.account_creditors + ':' + account_name
                    pass
                else:
                    raise Exception("Plugin \"share\" doesn't work on transactions that has both income and expense: please split it up into two.")

                new_entry, new_account = share_expenses(entry, config)

                new_entries.append(new_entry)
                new_accounts.add(new_account)
                continue

        # deep else:
        new_entries.append(entry)

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


def share_expenses(entry: Transaction, config: Config) -> Transaction:
    new_postings = []
    for posting in entry.postings:
        if re.match('Expenses:', posting.account):
            number = posting.units.number
            adjusted_posting = posting._replace(
                units=posting.units._replace(number=(number * config.fraction).quantize(config.quantize))
            )

            shared_meta = posting.meta.copy() if posting.meta else {}
            shared_meta.update(config.meta)
            shared_posting = Posting(
                config.account_share,
                units=posting.units._replace(number=(number * (ONE - config.fraction)).quantize(config.quantize)),
                cost=posting.cost,
                price=None,
                flag=None,
                meta=shared_meta
            )

            new_postings.append(adjusted_posting, shared_posting)

        else:
            new_postings.append(posting)

    # For the share account, group the postings together.
    grouped_postings = group_postings(new_postings, config.account_share)

    return entry._replace(postings=grouped_postings)
