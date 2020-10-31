"""
Plugin for Beancount to share expenses.

Credits: Based on Martin Blais <blais@furius.ca> personal snippet: https://github.com/beancount/beancount/issues/474.
"""
__author__ = "Akuukis"

from datetime import date, datetime
from typing import NamedTuple, Set, List, Union, Tuple
from collections import namedtuple
import re

from beancount.core.inventory import Inventory
from beancount.core.number import D, Decimal, ONE
from beancount.core.amount import Amount
from beancount.core.data import Account, Entries, Posting, Open, Transaction, new_metadata

from beancount_share.common import read_config, normalize_marked_txn, marked_postings, sum_income, sum_expenses
import beancount_share.metaset as metaset

__plugins__ = ('share',)

# pylint: disable=raising-non-exception

Config = NamedTuple('Config', [
    ('mark_name', str),
    ('meta_name', Union[str, None]),
    ('account_debtors', str),
    ('account_creditors', str),
    ('quantize', Decimal),
    ('open_date', Union[date, None]),
])

PluginShareParseError = namedtuple('LoadError', 'source message entry')


def share(entries: Entries, unused_options_map, config_string="{}") -> Tuple[Entries, List[Exception]]:
    new_accounts: Set[Account] = set()
    new_entries: Entries = []
    errors: List[PluginShareParseError] = []

    # 1. Parse config
    config_obj = read_config(config_string)
    raw_open_date = config_obj.pop('open_date', '1970-01-01')
    config = Config(
        config_obj.pop('mark_name'         , 'share'),
        config_obj.pop('meta_name'         , 'shared'),
        config_obj.pop('account_debtors'   , 'Assets:Debtors'),
        config_obj.pop('account_creditors' , 'Liabilities:Creditors'),
        D(str(config_obj.pop('quantize'    , 0.01))),
        None if raw_open_date is None else date.fromisoformat(raw_open_date),
    )

    for entry in entries:
        if not isinstance(entry, Transaction):
            new_entries.append(entry)
            continue

        # 2. Normalize marks.
        tx = normalize_marked_txn(entry, config.mark_name)

        # 3. Determine whenever this is debtor or creditor transactions.
        account_prefix: str
        total_income = sum_income(tx)
        total_expenses = sum_expenses(tx)
        total_value: Amount
        if(not total_expenses.is_empty() and total_income.is_empty()):
            account_prefix = config.account_debtors + ':'
            total_value = total_expenses.get_currency_units(tx.postings[0].units.currency)
        elif(total_expenses.is_empty() and not total_income.is_empty()):
            account_prefix = config.account_creditors + ':'
            total_value = total_income.get_currency_units(tx.postings[0].units.currency)
        else:
            errors.append(PluginShareParseError(
                new_metadata(entry.meta['filename'], entry.meta['lineno']),
                "Plugin \"share\" doesn't work on transactions that has both income and expense: please split it up into two transactions instead.",
                entry,
            ))
            new_entries.append(entry)
            continue

        # 4. Per posting, split it up based on marks.
        new_postings = []
        for marks, posting, orig, tx_clean in marked_postings(tx, config.mark_name, ("Income", "Expenses")):

            # 4.1. or skip if not marked.
            if(marks == None):
                new_postings.append(posting)
                continue

            if(not (posting.account.split(':')[0] in ("Income", "Expenses"))):
                errors.append(PluginShareParseError(
                    new_metadata(posting.meta['filename'], posting.meta['lineno']),
                    'Mark "share" doesn\'t make sense on a "{}" type posting.'.format(posting.account.split(':')[0]),
                    entry,
                ))
                new_postings.append(orig)
                continue

            # 5. Per mark, create a new posting.
            todo_absolute: List[Tuple[Amount, str]] = list()
            todo_percent: List[Tuple[float, str]] = list()
            todo_absent: List[str] = list()
            for mark in marks:
                parts = mark.split('-')
                account: str

                # 5.1. Apply defaults.
                try:
                    account = parts[0] if ':' in parts[0] else account_prefix + parts[0]
                    new_accounts.add(account)

                except IndexError:
                    errors.append(PluginShareParseError(
                        new_metadata(posting.meta['filename'], posting.meta['lineno']),
                        "Mark \"{}\" must contain account name.".format(mark),
                        entry,
                    ))
                    new_postings.append(orig)
                    continue

                if(len(parts) > 1):
                    if('%' in parts[1] or 'p' in parts[1]):
                        try:
                            todo_percent.append((float(parts[1].split('%')[0].split('p')[0])/100, account))
                        except IndexError:
                            errors.append(PluginShareParseError(
                                new_metadata(posting.meta['filename'], posting.meta['lineno']),
                                "Something wrong with percent fraction \"{}\", please use a dot, e.g. \"33.3%\".".format(parts[1]),
                                entry,
                            ))
                            new_postings.append(orig)
                            continue
                    else:
                        try:
                            todo_absolute.append((Amount(D(parts[1]).quantize(config.quantize), posting.units.currency), account))
                        except IndexError:
                            errors.append(PluginShareParseError(
                                new_metadata(posting.meta['filename'], posting.meta['lineno']),
                                "Something wrong with absolute fraction \"{}\", please use a dot, e.g. \"33.3\".".format(parts[1]),
                                entry,
                            ))
                            new_postings.append(orig)
                            continue
                else:
                    todo_absent.append(account)

            total_shared_absolute = sum([amount.number for amount,_ in todo_absolute], D(0).quantize(config.quantize))
            total_shared_relative = sum([percent for percent,_ in todo_percent])

            if(total_shared_absolute > abs(total_value.number)):
                errors.append(PluginShareParseError(
                    new_metadata(posting.meta['filename'], posting.meta['lineno']),
                    "The posting can't share more than it's absolute value",
                    entry,
                ))
                new_postings.append(orig)
                continue

            if(total_shared_relative > 1):
                errors.append(PluginShareParseError(
                    new_metadata(posting.meta['filename'], posting.meta['lineno']),
                    "The posting can't share more percent than 100%.",
                    entry,
                ))
                new_postings.append(orig)
                continue

            if(total_shared_absolute == abs(total_value.number) and total_shared_relative > 0):
                errors.append(PluginShareParseError(
                    new_metadata(posting.meta['filename'], posting.meta['lineno']),
                    "It doesn't make sense to split a remaining amount of zero.",
                    entry,
                ))
                new_postings.append(orig)
                continue

            if(total_shared_relative == 1 and len(todo_absent) > 0):
                errors.append(PluginShareParseError(
                    new_metadata(posting.meta['filename'], posting.meta['lineno']),
                    "It doesn't make sense to further auto-split when amount is already split for full 100%.",
                    entry,
                ))
                new_postings.append(orig)
                continue


            new_postings_inner = []
            # 5.2. Handle absolute amounts first: mutate original posting's amount & create new postings.
            for amount, account in todo_absolute:
                posting = posting._replace(
                    units=posting.units._replace(number=(posting.units.number - amount.number).quantize(config.quantize)),
                )
                if config.meta_name is not None:
                    posting = posting._replace(meta=metaset.add(posting.meta, config.meta_name, account + " " + amount.to_string()))
                new_postings_inner.append(Posting(
                    account,
                    units=posting.units._replace(number=(amount.number).quantize(config.quantize)),
                    cost=posting.cost,
                    price=None,
                    flag=None,
                    meta={} if config.meta_name is None else {config.meta_name: posting.account + " " + amount.to_string()}
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
                    meta={} if config.meta_name is None else {config.meta_name: posting.account + " " + str(int(percent * 100))+'% (' + units.to_string() + ')'}
                ))
                if config.meta_name is not None:
                    posting = posting._replace(meta=metaset.add(posting.meta, config.meta_name, account + " " + str(int(percent * 100))+'% (' + units.to_string() + ')'))

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
                    meta={} if config.meta_name is None else {config.meta_name: posting.account + " (" + str(int(percent * 100))+'%, ' + units.to_string() + ')'}
                ))
                if config.meta_name is not None:
                    posting = posting._replace(meta=metaset.add(posting.meta, config.meta_name, account + " (" + str(int(percent * 100))+'%, ' + units.to_string() + ')'))

            # 5.5. Handle original posting last (mutate!).
            posting = posting._replace(
                units=posting.units._replace(number=(remainder.number - total).quantize(config.quantize))
            )

            # if(posting.units.number > D(0)):
            new_postings.append(posting)

            new_postings.extend(new_postings_inner)

        for account in new_accounts:
            new_postings = group_postings(new_postings, account, config.meta_name)

        new_entries.append(tx_clean._replace(
            postings=new_postings,
        ))


    for account in sorted(new_accounts):
        new_meta = new_metadata(entries[0].meta['filename'], 0)
        open_entry = Open(new_meta, config.open_date, account, None, None)
        new_entries.append(open_entry)

    return new_entries, errors


def group_postings(postings: List[Posting], account: Account, meta_name: Union[str, None]) -> List[Posting]:
    grouped_postings = []
    share_postings = []
    share_balance = Inventory()
    meta = dict()
    for posting in postings:
        if posting.account == account:
            share_postings.append(posting)
            share_balance.add_position(posting)
            if(len(meta) == 0):
                meta = posting.meta
            elif(meta_name is not None):
                for mark in metaset.get(posting.meta, meta_name):
                    share_postings[0] = share_postings[0]._replace(meta=metaset.add(share_postings[0].meta, meta_name, mark))
        else:
            grouped_postings.append(posting)

    if share_postings:
        for pos in share_balance:
            grouped_postings.append(Posting(account, pos.units, pos.cost, None, None, share_postings[0].meta))

    return grouped_postings
