"""
Plugin for Beancount to share expenses.

Credits: Based on Martin Blais <blais@furius.ca> personal snippet: https://github.com/beancount/beancount/issues/474.
"""
__author__ = "Akuukis"

from datetime import date, datetime
from typing import NamedTuple, Set, List, Union, Tuple
from collections import namedtuple

from beancount.core.inventory import Inventory
from beancount.core.number import D, Decimal, ONE
from beancount.core.amount import Amount
from beancount.core.data import (
    Account,
    Entries,
    Posting,
    Open,
    Transaction,
    new_metadata,
)

from beancount_plugin_utils import metaset, marked
from beancount_plugin_utils.merge_postings import merge_postings
from beancount_plugin_utils.parse_config_string import parse_config_string
from beancount_plugin_utils.BeancountError import plugin_error_handler, posting_error_handler

from beancount_share.utils import sum_income, sum_expenses

__plugins__ = ["share"]

# pylint: disable=raising-non-exception


class Config(NamedTuple):
    mark_name: str = "share"
    meta_name: Union[str, None] = "shared"
    account_debtors: str = "Assets:Debtors"
    account_creditors: str = "Liabilities:Creditors"
    quantize: Decimal = D("0.01")
    open_date: Union[date, None] = date.fromisoformat("1970-01-01")


PluginShareError = namedtuple("PluginShareError", "source message entry")


new_accounts: Set[Account] = set()


def share(entries: Entries, unused_options_map, config_string="{}") -> Tuple[Entries, List[NamedTuple]]:
    new_entries: Entries = []
    errors: List[NamedTuple] = []

    # 1. Parse config
    with plugin_error_handler(entries, new_entries, errors, "share", PluginShareError):
        config = load_config(config_string)

        new_entries[:], errors[:] = marked.on_marked_transactions(
            per_marked_transaction,
            entries,
            config,
            config.mark_name,
            ("Income", "Expenses"),
            PluginShareError,
        )

        if config.open_date != None:
            for account in sorted(new_accounts):
                new_meta = new_metadata(entries[0].meta["filename"], 0)
                open_entry = Open(new_meta, config.open_date, account, None, None)
                new_entries.append(open_entry)

    return new_entries, errors


def load_config(config_string: str) -> Config:
    ############################################################################
    #### Load config (optional)

    # 1. Parse config string. Just copy/paste this block.
    config_dict = parse_config_string(config_string)

    # 2. Apply transforms (e.g. from `str` to `date`) where needed.
    # Wrap each transform separately with a nice error message.
    try:
        if "open_date" in config_dict:
            config_dict["open_date"] = (
                None if config_dict["open_date"] is None else date.fromisoformat(config_dict["open_date"])
            )
    except:
        raise RuntimeError('Bad "open_date" value - it must be a valid date, formatted in UTC (e.g. "2000-01-01").')

    # 3. Create config itself. Just copy/paste this block. Done!
    return Config(**config_dict)


def per_marked_transaction(tx: Transaction, tx_orig: Transaction, config: Config) -> List[Transaction]:
    account_prefix: str
    total_income = sum_income(tx)
    total_expenses = sum_expenses(tx)
    total_value: Amount

    if not total_expenses.is_empty() and total_income.is_empty():
        account_prefix = config.account_debtors + ":"
        total_value = total_expenses.get_currency_units(tx.postings[0].units.currency)
    elif total_expenses.is_empty() and not total_income.is_empty():
        account_prefix = config.account_creditors + ":"
        total_value = total_income.get_currency_units(tx.postings[0].units.currency)
    else:
        raise RuntimeError(
            'Plugin "share" doesn\'t work on transactions that has both income and expense: please split it up into two transactions instead.'
        )

    # 4. Per posting, split it up based on marks.
    new_postings = []
    for posting in tx.postings:
        with posting_error_handler(tx_orig, posting, PluginShareError):
            new_postings.extend(per_marked_posting(posting, config, account_prefix, total_value))

    for account in new_accounts:
        new_postings = merge_postings(account, new_postings, config.meta_name)

    return [tx._replace(postings=new_postings)]


def per_marked_posting(posting: Posting, config: Config, account_prefix: str, total_value: Amount):
    marks = metaset.get(posting.meta, config.mark_name)

    # 4.1. or skip if not marked.
    if len(marks) == 0:
        return [posting]

    # 5. Per mark, create a new posting.
    todo_absolute: List[Tuple[Amount, str]] = list()
    todo_percent: List[Tuple[float, str]] = list()
    todo_absent: List[str] = list()
    for mark in marks:
        parts = mark.split("-")
        account: str

        # 5.1. Apply defaults.
        if parts[0] == "":
            raise RuntimeError('Plugin "share" requires mark to contain account name, seperated with "-".')

        account = parts[0] if ":" in parts[0] else account_prefix + parts[0]
        new_accounts.add(account)

        if len(parts) > 1:
            if "%" in parts[1] or "p" in parts[1]:
                try:
                    todo_percent.append(
                        (
                            float(parts[1].split("%")[0].split("p")[0]) / 100,
                            account,
                        )
                    )
                except Exception:
                    raise RuntimeError(
                        'Something wrong with relative fraction "{}", please use a dot, e.g. "33.33p".'.format(parts[1])
                    )
            else:
                try:
                    todo_absolute.append(
                        (
                            Amount(
                                D(parts[1]).quantize(config.quantize),
                                posting.units.currency,
                            ),
                            account,
                        )
                    )
                except Exception:
                    raise RuntimeError(
                        'Something wrong with absolute fraction "{}", please use a dot, e.g. "2.50".'.format(parts[1])
                    )
        else:
            todo_absent.append(account)

    total_shared_absolute = sum(
        [amount.number for amount, _ in todo_absolute],
        D(0).quantize(config.quantize),
    )
    total_shared_relative = sum([percent for percent, _ in todo_percent])

    if total_shared_absolute > abs(total_value.number):
        raise RuntimeError("The posting can't share more than it's absolute value")

    if total_shared_relative > 1:
        raise RuntimeError(
            "The posting can't share more percent than 100%.",
        )

    if total_shared_absolute == abs(total_value.number) and total_shared_relative > 0:
        raise RuntimeError("It doesn't make sense to split a remaining amount of zero.")

    if total_shared_relative == 1 and len(todo_absent) > 0:
        raise RuntimeError("It doesn't make sense to further auto-split when amount is already split for full 100%.")

    new_postings_inner = []
    # 5.2. Handle absolute amounts first: mutate original posting's amount & create new postings.
    for amount, account in todo_absolute:
        posting = posting._replace(
            units=posting.units._replace(number=(posting.units.number - amount.number).quantize(config.quantize)),
        )
        if config.meta_name is not None:
            posting = posting._replace(
                meta=metaset.add(posting.meta, config.meta_name, account + " " + amount.to_string())
            )
        new_postings_inner.append(
            Posting(
                account,
                units=posting.units._replace(number=(amount.number).quantize(config.quantize)),
                cost=posting.cost,
                price=None,
                flag=None,
                meta={} if config.meta_name is None else {config.meta_name: posting.account + " " + amount.to_string()},
            )
        )

    # 5.3. Handle relative amounts second: create new postings.
    remainder = posting.units
    total = D(0)
    for percent, account in todo_percent:
        units = posting.units._replace(number=(D(float(remainder.number) * percent)).quantize(config.quantize))
        total = total + units.number
        new_postings_inner.append(
            Posting(
                account,
                units=units,
                cost=posting.cost,
                price=None,
                flag=None,
                meta={}
                if config.meta_name is None
                else {
                    config.meta_name: posting.account + " " + str(int(percent * 100)) + "% (" + units.to_string() + ")"
                },
            )
        )
        if config.meta_name is not None:
            posting = posting._replace(
                meta=metaset.add(
                    posting.meta,
                    config.meta_name,
                    account + " " + str(int(percent * 100)) + "% (" + units.to_string() + ")",
                )
            )

    # 5.4. Handle absent amounts third: create new postings.
    total_percent = sum(i for i, _ in todo_percent)
    percent = (1 - total_percent) / (1 + len(todo_absent))
    for account in todo_absent:
        units = posting.units._replace(number=(D(float(remainder.number) * percent)).quantize(config.quantize))
        total = total + units.number
        new_postings_inner.append(
            Posting(
                account,
                units=units,
                cost=posting.cost,
                price=None,
                flag=None,
                meta={}
                if config.meta_name is None
                else {
                    config.meta_name: posting.account + " (" + str(int(percent * 100)) + "%, " + units.to_string() + ")"
                },
            )
        )
        if config.meta_name is not None:
            posting = posting._replace(
                meta=metaset.add(
                    posting.meta,
                    config.meta_name,
                    account + " (" + str(int(percent * 100)) + "%, " + units.to_string() + ")",
                )
            )

    # 5.5. Handle original posting last (mutate!).
    posting = posting._replace(
        units=posting.units._replace(number=(remainder.number - total).quantize(config.quantize)),
        meta=metaset.clear(posting.meta, config.mark_name),
    )

    # if(posting.units.number > D(0)):
    #     new_postings.append(posting)

    return [posting] + new_postings_inner
