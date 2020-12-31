from beancount.core.data import Transaction
from beancount.core.inventory import Inventory


def sum_income(tx: Transaction) -> Inventory:
    total = Inventory()
    for posting in tx.postings:
        if posting.account.split(":")[0] == "Income":
            total.add_position(posting)
    return total


def sum_expenses(tx: Transaction) -> Inventory:
    total = Inventory()
    for posting in tx.postings:
        if posting.account.split(":")[0] == "Expenses":
            total.add_position(posting)
    return total
