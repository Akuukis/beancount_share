Feature: Shortcuts for marking postings

    Background: default
        Given this config:
            {}
        Given the following setup:
            2020-01-01 open Assets:Cash
            2020-01-01 open Expenses:Food:Drinks

    Scenario: Transaction meta translates to meta for every applicable posting without their own share- meta (positive case)
        When this transaction is processed:
            2020-01-01 * "BarAlice" "Lunch with friend Bob"
                share: "Bob-4"
                Assets:Cash               -10.00 USD
                Expenses:Food:Drinks

        Then the original transaction should be modified:
            2020-01-01 * "BarAlice" "Lunch with friend Bob"
                Assets:Cash               -10.00 USD
                Expenses:Food:Drinks        6.00 USD
                    shared: "Assets:Debtors:Bob 4.00 USD"
                Assets:Debtors:Bob          4.00 USD
                    shared: "Expenses:Food:Drinks 4.00 USD"

    Scenario: Transaction meta translates to meta for every applicable posting without their own share- meta (negative case)
        When this transaction is processed:
            2020-01-01 * "BarAlice" "Lunch with friend Bob"
                share: "Bob-9"
                Assets:Cash               -10.00 USD
                Expenses:Food:Drinks
                    share: "Bob-4"

        Then the original transaction should be modified:
            2020-01-01 * "BarAlice" "Lunch with friend Bob"
                Assets:Cash               -10.00 USD
                Expenses:Food:Drinks        6.00 USD
                    shared: "Assets:Debtors:Bob 4.00 USD"
                Assets:Debtors:Bob          4.00 USD
                    shared: "Expenses:Food:Drinks 4.00 USD"

    Scenario: Tags are translated and appended to transaction meta
        When this transaction is processed:
            2020-01-01 * "BarAlice" "Lunch with friend Bob" #share-Bob-4
                Assets:Cash               -10.00 USD
                Expenses:Food:Drinks

        Then the original transaction should be modified:
            2020-01-01 * "BarAlice" "Lunch with friend Bob"
                Assets:Cash               -10.00 USD
                Expenses:Food:Drinks        6.00 USD
                    shared: "Assets:Debtors:Bob 4.00 USD"
                Assets:Debtors:Bob          4.00 USD
                    shared: "Expenses:Food:Drinks 4.00 USD"
