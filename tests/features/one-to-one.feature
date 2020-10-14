Feature: Share a single posting to single account

    Background: Simple case without config
        Given this config:
            {}

    Scenario: Partially share sole Expense posting using absolute amount
        When this transaction is processed:
            2020-01-01 * "BarAlice" "Lunch with friend Bob"
                Assets:Cash               -10.00 USD
                Expenses:Food:Drinks
                    share: "Assets:Debtors:Bob-4"

        Then the original transaction should be modified:
            2020-01-01 * "BarAlice" "Lunch with friend Bob"
                Assets:Cash               -10.00 USD
                Expenses:Food:Drinks        6.00 USD
                    shared: "Assets:Debtors:Bob 4 USD"
                Assets:Debtors:Bob          4.00 USD
                    shared: "Expenses:Food:Drinks 4 USD"

    Scenario: Partially share sole Expense posting with short account name
        When this transaction is processed:
            2020-01-01 * "BarAlice" "Lunch with friend Bob"
                Assets:Cash               -10.00 USD
                Expenses:Food:Drinks
                    share: "Assets:Debtors:Bob-4"

        Then the original transaction should be modified:
            2020-01-01 * "BarAlice" "Lunch with friend Bob"
                Assets:Cash               -10.00 USD
                Expenses:Food:Drinks        6.00 USD
                    shared: "Assets:Debtors:Bob 4 USD"
                Assets:Debtors:Bob          4.00 USD
                    shared: "Expenses:Food:Drinks 4 USD"

    Scenario: Partially share sole Expense posting using relative amount
        When this transaction is processed:
            2020-01-01 * "BarAlice" "Lunch with friend Bob"
                Assets:Cash               -10.00 USD
                Expenses:Food:Drinks
                    share: "Bob-40%"

        Then the original transaction should be modified:
            2020-01-01 * "BarAlice" "Lunch with friend Bob"
                Assets:Cash               -10.00 USD
                Expenses:Food:Drinks        6.00 USD
                    shared: "Assets:Debtors:Bob 40% (4 USD)"
                Assets:Debtors:Bob          4.00 USD
                    shared: "Expenses:Food:Drinks 40% (4 USD)"

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
                    shared: "Assets:Debtors:Bob (50%, 5 USD)"
                Assets:Debtors:Bob          5.00 USD
                    shared: "Expenses:Food:Drinks (50%, 5 USD)"

    Scenario: Fully share sole Expense posting using absolute amount
        When this transaction is processed:
            2020-01-01 * "BarAlice" "Lunch with friend Bob"
                Assets:Cash               -10.00 USD
                Expenses:Food:Drinks
                    share: "Bob-10"

        Then the original transaction should be modified:
            2020-01-01 * "BarAlice" "Lunch with friend Bob"
                Assets:Cash               -10.00 USD
                Expenses:Food:Drinks        0.00 USD
                    shared: "Assets:Debtors:Bob 10 USD"
                Assets:Debtors:Bob         10.00 USD
                    shared: "Expenses:Food:Drinks 10 USD"

    Scenario: Fully share sole Expense posting using relative amount
    Scenario: Share sole Income posting
    Scenario: Share one of several postings
    Scenario: Throw Error if sharing a non-applicable posting (Assets, Liabilities or Equity)
