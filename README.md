Share
===============================================================================

[![PyPI - Version](https://img.shields.io/pypi/v/beancount_share)](https://pypi.org/project/packages/beancount_share/)
![PyPI - Downloads](https://img.shields.io/pypi/dm/beancount_share)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/beancount_share)
![PyPI - License](https://img.shields.io/pypi/l/beancount_share)

One beancount plugin to share expenses among multiple partners within one ledger.



Install
===============================================================================

```
pip3 install beancount_share --user
```

Or copy to path used for python. For example, `$HOME/.local/lib/python3.7/site-packages/beancount_share/*` would do on Debian. If in doubt, look where `beancount` folder is and copy next to it.




How to Use
===============================================================================

> Please read the elaborate version at the Beancount docs: https://docs.google.com/document/d/1MjSpGoJVdgyg8rhKD9otSKo4iSD2VkSYELMWDBbsBiU/edit


First, add a simple configuration:

```
plugin "beancount_share" "{
    "tag": "bob",
    "fraction": 0.50,
    "account_share": "Assets:Debtors:Bob",
}"
```

Then, your transactions tagged with `#Bob` like this...

```
2020-01-01 * "BarAlice" "Lunch with friend Bob" #bob
    Assets:Cash               -10.00 USD
    Expenses:Food:Drinks
```

will get transformed to transactions like this:

```
2020-01-01 * "BarAlice" "Lunch with friend Bob" #bob
    Assets:Cash               -10.00 USD
    Expenses:Food:Drinks        5.00 USD
    Assets:Debtors:Bob          5.00 USD
```

Development
===============================================================================

Please see Makefile and inline comments.
