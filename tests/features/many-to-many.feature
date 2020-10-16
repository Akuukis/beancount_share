Feature: Share several postings to several accounts

  Background: Simple case without config
    Given this config:
      {}

  Scenario: Share all applicable postings to several overlapping accounts
    When this transaction is processed:
      2020-01-01 * "BarAlice" "Lunch with my guy friends"
        Assets:Cash           -24.00 EUR
        Expenses:Food:Lunch    17.00 EUR
          share: "Bob-7"
          share2: "Charlie"
        Expenses:Food:Drinks
          share: "Bob"
          share2: "Charlie-3"

    Then the original transaction should be modified:
      2020-01-01 * "BarAlice" "Lunch with my guy friends"
        Assets:Cash             -24.00 EUR
        Expenses:Food:Lunch       5.00 EUR
          shared: "Assets:Debtors:Bob 7.00 EUR"
          shared901: "Assets:Debtors:Charlie (50%, 5.00 EUR)"
        Expenses:Food:Drinks      2.00 EUR
          shared: "Assets:Debtors:Charlie 3.00 EUR"
          shared901: "Assets:Debtors:Bob (50%, 2.00 EUR)"
        Assets:Debtors:Bob        9.00 EUR
          shared: "Expenses:Food:Lunch 7.00 EUR"
          shared901: "Expenses:Food:Drinks (50%, 2.00 EUR)"
        Assets:Debtors:Charlie    8.00 EUR
          shared: "Expenses:Food:Lunch (50%, 5.00 EUR)"
          shared901: "Expenses:Food:Drinks 3.00 EUR"

  Scenario: Share several applicable postings to several overlapping accounts
    When this transaction is processed:
      2020-01-01 * "BarAlice" "Lunch with my guy friends"
        Assets:Cash           -25.00 EUR
        Expenses:Food:Snacks    1.00 EUR
        Expenses:Food:Lunch    17.00 EUR
          share: "Bob-7"
          share2: "Charlie"
        Expenses:Food:Drinks
          share: "Bob"
          share2: "Charlie-3"

    Then the original transaction should be modified:
      2020-01-01 * "BarAlice" "Lunch with my guy friends"
        Assets:Cash             -25.00 EUR
        Expenses:Food:Snacks      1.00 EUR
        Expenses:Food:Lunch       5.00 EUR
          shared: "Assets:Debtors:Bob 7.00 EUR"
          shared901: "Assets:Debtors:Charlie (50%, 5.00 EUR)"
        Expenses:Food:Drinks      2.00 EUR
          shared: "Assets:Debtors:Charlie 3.00 EUR"
          shared901: "Assets:Debtors:Bob (50%, 2.00 EUR)"
        Assets:Debtors:Charlie    8.00 EUR
          shared: "Expenses:Food:Lunch (50%, 5.00 EUR)"
          shared901: "Expenses:Food:Drinks 3.00 EUR"
        Assets:Debtors:Bob        9.00 EUR
          shared: "Expenses:Food:Lunch 7.00 EUR"
          shared901: "Expenses:Food:Drinks (50%, 2.00 EUR)"

  Scenario: Throw Error if sharing both Expense and Income postings
