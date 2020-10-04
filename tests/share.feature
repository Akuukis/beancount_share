Feature: Share expenses with other people easily

    Scenario: Readme example

        Given the following beancount transaction:
            ;
            2020-01-01 * "BarAlice" "Lunch with friend Bob" #bob
                Assets:Cash               -10.00 USD
                Expenses:Food:Drinks

        When the beancount_share plugin is executed with config:
            {
                "tag": "bob",
                "fraction": 0.50,
                "account_share": "Assets:Debtors:Bob",
            }

        Then the original transaction should be modified:
            ;
            2020-01-01 * "BarAlice" "Lunch with friend Bob" #bob
                Assets:Cash               -10.00 USD
                Expenses:Food:Drinks        5.00 USD
                Assets:Debtors:Bob          5.00 USD

    Scenario: Beancount docs example

        Given the following beancount transaction:
            ;
            2018-12-23 * "WHISK" "Water refill" #carolyn
                Liabilities:US:Amex:BlueCash  -32.66 USD
                Expenses:Food:Grocery

        When the beancount_share plugin is executed with config:
            {
                "tag": "carolyn",
                "fraction": 0.60,
                "account_share": "Assets:US:Share:Carolyn",
                "meta": {"share": True}
            }

        Then the original transaction should be modified:
            ;
            2018-12-23 * "WHISK" "Water refill" #carolyn
                Liabilities:US:Amex:BlueCash  -32.66 USD
                Expenses:Food:Grocery          19.60 USD
                Assets:US:Share:Carolyn        13.06 USD
                    share: TRUE
