Share
===============================================================================

[![PyPI - Version](https://img.shields.io/pypi/v/beancount_share)](https://pypi.org/project/beancount-share/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/beancount_share)](https://pypi.org/project/beancount-share/)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/beancount_share)](https://pypi.org/project/beancount-share/)
[![License](https://img.shields.io/pypi/l/beancount_share)](https://choosealicense.com/licenses/agpl-3.0/)
[![Linting](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A beancount plugin to share expenses among multiple partners within one ledger.

`#share` plugin uses tag syntax to add info to the transaction:
- basic: share expense with another partner 50%-50% - simply use `#share-Bob`
- amount: share a specific sum of expense with another partner - use `#share-Bob-7`
- percentage: share a specific percentage of expense with another partner - use `#share-Bob-40p`
- many: share expense with multiple partners - use `#share-Bob #share-Charlie`

This plugin is very powerful and most probably can deal with all of your sharing needs.








Install
===============================================================================

```
pip3 install beancount_share --user
```

Or copy to path used for python. For example, `$HOME/.local/lib/python3.7/site-packages/beancount_share/*` would do on Debian. If in doubt, look where `beancount` folder is and copy next to it.








Setup
===============================================================================

> Please read the elaborate version at the [Beancount docs](https://docs.google.com/document/d/1MjSpGoJVdgyg8rhKD9otSKo4iSD2VkSYELMWDBbsBiU/edit).

Add the plugin like this:

```
plugin "beancount_share" "{}"
```

Done. If you want to use custom configuration (read below), then you put it inside those `{}` brackets.








Usecase: split expense with "Bob" equally.
===============================================================================
> TL;DR: use `#share-Bob` tag.

If you, Alice, have had a nice evening out and are in a equal relationship with Bob, you most probably will use the basic share tag that includes only a name: `#share-Bob`.

The default share tag splits transaction into 2 transactions equally to you and your debtor.




How to use
-----------------------------------------------------------------------

Tag your transaction simply with a tag + name, like `#share-Bob`:

```
2020-01-01 * "BarAlice" "Lunch with friend Bob" #share-Bob
    Assets:Cash               -10.00 USD
    Expenses:Food:Drinks
```




What happens
-----------------------------------------------------------------------

The transaction will get transformed into 2 transactions each with 50% of the sum.
The name in the tag will become your debtor (or creditor, if splitting an income).

```
2020-01-01 * "BarAlice" "Lunch with friend Bob"
    Assets:Cash               -10.00 USD
    Expenses:Food:Drinks        5.00 USD
        shared: "Assets:Debtors:Bob (50%, 5.00 USD)"
    Assets:Debtors:Bob          5.00 USD
        shared: "Expenses:Food:Drinks (50%, 5.00 USD)"
```








Usecase: split expense with "Bob" for a specific amount.
===============================================================================
> TL;DR: use `#share-Bob-7` tag.

If you, Alice, have had a nice evening out, and payed also for your friends dinner and he promised to pay you back later, he became your debtor.
You should tag the expense with his name + the sum he owes you: `#share-Bob-7`.

The amount share tag splits transaction into 2 transactions where your debtors' part is the amount specified and yours - all the rest.




How to use
-----------------------------------------------------------------------

Tag your transaction with a tag + name + debtors' amount:

```
2020-01-01 * "BarAlice" "Dinner with friend Bob" #share-Bob-7
    Assets:Cash               -10.00 USD
    Expenses:Food:Drinks
```




What happens
-----------------------------------------------------------------------

The transaction will get transformed into 2 transactions. Your debtors' transaction with the specific amount, yours - with all the rest of the sum.

```
2020-01-01 * "BarAlice" "Dinner with friend Bob"
    Assets:Cash               -10.00 EUR
    Expenses:Food:Drinks        3.00 EUR
        shared: "Assets:Debtors:Bob 7.00 EUR"
    Assets:Debtors:Bob          7.00 EUR
        shared: "Expenses:Food:Drinks 7.00 EUR"
```








Usecase: split expense with "Bob" for a specific percentage.
===============================================================================
> TL;DR: use  `#share-Bob-40%` tag.

For example, you, Alice, have had a few drinks with a friend Bob and payed also for his beer.
You both don't remember all the pennies who owns who, but you know that you drank a bit more.
That means you end up with a proportion that he ows you.
You should tag the expense with his name + the percentage of expense he owes you: `#share-Bob-40%`.

The percentage share tag splits transaction into 2 transactions where your debtors part is the percentage specified and yours - all the rest.




How to use
-----------------------------------------------------------------------

Tag your transaction with a tag + name + debtors' percentage:

```
2020-01-01 * "BarAlice" "Drinks with friend Bob" #share-Bob-40p
    Assets:Cash               -10.00 USD
    Expenses:Food:Drinks
```

Note: do not forget to add `p` (a **p**ercent, but beancount doesn't allow "%" sign itself), otherwise it will be considered an amount tag!




What happens
-----------------------------------------------------------------------

The transaction will get transformed into 2 transactions. Your debtors' transaction with the sum of specified percentage, yours - with all the rest of the sum.

```
2020-01-01 * "BarAlice" "Drinks with friend Bob"
    Assets:Cash               -10.00 EUR
    Expenses:Food:Drinks        6.00 EUR
        shared: "Assets:Debtors:Bob 40% (4.00 EUR)"
    Assets:Debtors:Bob          4.00 EUR
        shared: "Expenses:Food:Drinks 40% (4.00 EUR)"
```








Usecase: split expense with multiple people - "Bob" and "Charlie" - equally.
===============================================================================
> Tl;DR: use `#share-Bob #share-Charlie` tag.

If you, Alice, had a few drinks with 2 of your guy friends Bob and Charlie.
You payed for their beer and they became your debtors.
You all like the Mediterrian style of money splitting, so you spilt the evening expenses equally.
You should add 2 tags to the expense, each with a friend's name: `#share-Bob` and `#share-Charlie`.




How to use
-----------------------------------------------------------------------

Tag your transaction with a tag for each person you want to split the transaction with: tag + name:

```
2020-01-01 * "BarAlice" "Beer with my guy friends" #share-Bob #share-Charlie
    Assets:Cash               -10.00 USD
    Expenses:Food:Drinks
```




What happens
-----------------------------------------------------------------------

The transaction will get transformed into as many transactions as tags you have added + your own.
The amount will be spilt equally between all of you.

```
2020-01-01 * "BarAlice" "Beer with my guy friends"
    Assets:Cash               -10.00 EUR
    Expenses:Food:Drinks        3.34 EUR
        shared: "Assets:Debtors:Bob (33%, 3.33 EUR)"
        shared901: "Assets:Debtors:Charlie (33%, 3.33 EUR)"
    Assets:Debtors:Bob          3.33 EUR
        shared: "Expenses:Food:Drinks (33%, 3.33 EUR)"
    Assets:Debtors:Charlie      3.33 EUR
        shared: "Expenses:Food:Drinks (33%, 3.33 EUR)"
```








Usecase: something complex.
===============================================================================
> TL;DR: nope, read on.

In reality, tags are only the shortcuts of share plugin to make your life easier.
You can always write out the full transaction and sometimes it does make more sense.

This is an example of a super complex case that might be easier to write out in full syntax:

You, Alice are a party and had drinks with friends.
You payed for the whole party, but your friends are quite pricky and each has their own specific ways how to count what to repay you.
Bob will give you back an amount of his beer, Charlie is a getleman and wants to pay for the half of all the rest and David just does not care and is ok to spilt in half with you what's left.

This leaves us with 3 different metas to our transaction:
`Bob-4`, `Charlie-50%`, `David`




How to use
-----------------------------------------------------------------------

Instead of adding tags, you might want to explicitly add meta to the transaction:

```
2020-01-01 * "BarAlice" "Beer with my guy friends"
    Assets:Cash               -10.00 EUR
    Expenses:Food:Drinks
        share: "Bob-4"
        share2: "Charlie-50%"
        share3: "David"
```

To add many share metas, add a number for each `share` and add amont, percentage or nothing the same as with tags.




What happens
-----------------------------------------------------------------------

The plugin calculates amounts in complex transactions always in the same order:

The transaction will get transformed into as many transactions as metas you have added + your own.

The amount will be spilt by these rules in this order:
1. All absolute amounts are taken away;
2. The amount that is left now is 100%;
3. All specified percentages are taken away;
4. Everything that is left with default metas is split equally;

```
2020-01-01 * "BarAlice" "Beer with my many friends"
    Assets:Cash             -10.00 EUR
    Expenses:Food:Drinks      1.50 EUR
        shared: "Assets:Debtors:Bob 4.00 EUR"
        shared901: "Assets:Debtors:Charlie 50% (3.00 EUR)"
        shared902: "Assets:Debtors:David (25%, 1.50 EUR)"
    Assets:Debtors:Bob        4.00 EUR
        shared: "Expenses:Food:Drinks 4.00 EUR"
    Assets:Debtors:Charlie    2.40 EUR
        shared: "Expenses:Food:Drinks 50% (3.00 EUR)"
    Assets:Debtors:David      1.80 EUR
        shared: "Expenses:Food:Drinks (25%, 1.50 EUR)"
```




Configuration
===============================================================================

Note: **Do NOT use double-quotes within the configuration!** The configuration is a Python dict, not a JSON object.

This is the default configuration in full. Providing it equals to providing no configuration at all.

```
plugin "beancount_share" "{
    'mark_name': 'share',
    'meta_name': 'shared',
    'account_debtors': 'Assets:Debtors',
    'account_creditors': 'Liabilities:Creditors',
    'open_date': '1970-01-01',
    'quantize': '0.01'
}"
```

Note that `meta_name` and `open_date` may also be set to `None` - former to disable informative meta generation, and latter to disable `open` entry creation. Example:


```
plugin "beancount_share" "{
    'mark_name': 'share',
    'meta_name': None,
    'account_debtors': 'Assets:Debtors',
    'account_creditors': 'Liabilities:Creditors',
    'open_date': None,
    'quantize': '0.01'
}"
```








Tests
===============================================================================

If the examples above do not suffice your needs, check out the tests.
They consist of human-readable examples for more specific cases.








Development
===============================================================================

Please see Makefile and inline comments.
