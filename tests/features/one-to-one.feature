Feature: Share a single posting to single account

    Background: Simple case without config
        Given this config:
            {}

    Scenario: Partially share sole Expense posting using absolute amount
        When this transaction is processed:
            2020-01-01 * "BarAlice" "Lunch with friend Bob"
                Assets:Cash               -10.00 USD
                Expenses:Food:Drinks
                    share: "Bob-5"

        Then the original transaction should be modified:
            2020-01-01 * "BarAlice" "Lunch with friend Bob"
                Assets:Cash               -10.00 USD
                Expenses:Food:Drinks        5.00 USD
                    share: "Bob-5"
                Assets:Debtors:Bob          5.00 USD
                    share: "Bob-5"

    Scenario: Partially share sole Expense posting using relative amount
        When this transaction is processed:
            2020-01-01 * "BarAlice" "Lunch with friend Bob"
                Assets:Cash               -10.00 USD
                Expenses:Food:Drinks
                    share: "Bob-50%"

        Then the original transaction should be modified:
            2020-01-01 * "BarAlice" "Lunch with friend Bob"
                Assets:Cash               -10.00 USD
                Expenses:Food:Drinks        5.00 USD
                    share: "Bob-50%"
                Assets:Debtors:Bob          5.00 USD
                    share: "Bob-50%"

    Scenario: Partially share sole Expense posting using ommitted amount
        When this transaction is processed:
            2020-01-01 * "BarAlice" "Lunch with friend Bob"
                Assets:Cash               -10.00 USD
                Expenses:Food:Drinks
                    share: "Bob"

        Then the original transaction should be modified:
            2020-01-01 * "BarAlice" "Lunch with friend Bob"
                Assets:Cash               -10.00 USD
                Expenses:Food:Drinks        5.00 USD
                    share: "Bob"
                Assets:Debtors:Bob          5.00 USD
                    share: "Bob"

    Scenario: Fully share sole Expense posting using absolute amount
    Scenario: Fully share sole Expense posting using relative amount
    Scenario: Share sole Income posting
    Scenario: Share one of several postings
    Scenario: Throw Error if sharing a non-applicable posting (Assets, Liabilities or Equity)
