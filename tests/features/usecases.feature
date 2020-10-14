Feature: Share expenses with other people easily

    Scenario: Example in this Readme

        Given this config:
            {}

        When this transaction is processed:
            ;
            2020-01-01 * "BarAlice" "Lunch with friend Bob" #share-Bob
                Assets:Cash               -10.00 USD
                Expenses:Food:Drinks

        Then the original transaction should be modified:
            ;
            2020-01-01 * "BarAlice" "Lunch with friend Bob"
                Assets:Cash               -10.00 USD
                Expenses:Food:Drinks        5.00 USD
                Assets:Debtors:Bob          5.00 USD

    Scenario: Example in Beancount docs

        Given this config:
            {
                "account_debtors": "Assets:US:Share",
                "default_fraction": 0.4,
                "meta": {"share": True}
            }

        When this transaction is processed:
            ;
            2018-12-23 * "WHISK" "Water refill" #share-Carolyn
                Liabilities:US:Amex:BlueCash  -32.66 USD
                Expenses:Food:Grocery

        Then the original transaction should be modified:
            ;
            2018-12-23 * "WHISK" "Water refill"
                Liabilities:US:Amex:BlueCash  -32.66 USD
                Expenses:Food:Grocery          19.60 USD
                Assets:US:Share:Carolyn        13.06 USD
                    share: TRUE
