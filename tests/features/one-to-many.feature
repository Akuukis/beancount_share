Feature: Share a single posting to several accounts

  Background: default
    Given this config:
      {}
    Given the following setup:
      2020-01-01 open Assets:Cash
      2020-01-01 open Expenses:Food:Drinks

  Scenario: Share a posting to several different accounts using absolute amounts
    When this transaction is processed:
      2020-01-01 * "BarAlice" "Beer with my guy friends"
        Assets:Cash               -10.00 EUR
        Expenses:Food:Drinks
          share: "Bob-4"
          share2: "Charlie-4"

    Then should not error
    Then the original transaction should be modified:
      2020-01-01 * "BarAlice" "Beer with my guy friends"
        Assets:Cash               -10.00 EUR
        Expenses:Food:Drinks        2.00 EUR
          shared: "Assets:Debtors:Bob 4.00 EUR"
          shared901: "Assets:Debtors:Charlie 4.00 EUR"
        Assets:Debtors:Bob          4.00 EUR
          shared: "Expenses:Food:Drinks 4.00 EUR"
        Assets:Debtors:Charlie      4.00 EUR
          shared: "Expenses:Food:Drinks 4.00 EUR"

  Scenario: Share a posting to several different accounts using relative amounts
    When this transaction is processed:
      2020-01-01 * "BarAlice" "Beer with my guy friends"
        Assets:Cash               -10.00 EUR
        Expenses:Food:Drinks
          share: "Bob-40%"
          share2: "Charlie-40%"

    Then should not error
    Then the original transaction should be modified:
      2020-01-01 * "BarAlice" "Beer with my guy friends"
        Assets:Cash               -10.00 EUR
        Expenses:Food:Drinks        2.00 EUR
          shared: "Assets:Debtors:Bob 40% (4.00 EUR)"
          shared901: "Assets:Debtors:Charlie 40% (4.00 EUR)"
        Assets:Debtors:Bob          4.00 EUR
          shared: "Expenses:Food:Drinks 40% (4.00 EUR)"
        Assets:Debtors:Charlie      4.00 EUR
          shared: "Expenses:Food:Drinks 40% (4.00 EUR)"

  Scenario: Share a posting to several different accounts using omitted amount
    When this transaction is processed:
      2020-01-01 * "BarAlice" "Beer with my guy friends"
        Assets:Cash               -10.00 EUR
        Expenses:Food:Drinks
          share: "Bob"
          share2: "Charlie"

    Then should not error
    Then the original transaction should be modified:
      2020-01-01 * "BarAlice" "Beer with my guy friends"
        Assets:Cash               -10.00 EUR
        Expenses:Food:Drinks        3.34 EUR
          shared: "Assets:Debtors:Bob (33%, 3.33 EUR)"
          shared901: "Assets:Debtors:Charlie (33%, 3.33 EUR)"
        Assets:Debtors:Bob          3.33 EUR
          shared: "Expenses:Food:Drinks (33%, 3.33 EUR)"
        Assets:Debtors:Charlie      3.33 EUR
          shared: "Expenses:Food:Drinks (33%, 3.33 EUR)"

  Scenario: Share a posting to several different accounts using mixed amounts
    When this transaction is processed:
      2020-01-01 * "BarAlice" "Beer with my guy friends"
        Assets:Cash               -10.00 EUR
        Expenses:Food:Drinks
          share: "Bob-4"
          share2: "Charlie-40%"
          share3: "David"

    Then should not error
    Then the original transaction should be modified:
      2020-01-01 * "BarAlice" "Beer with my guy friends"
        Assets:Cash             -10.00 EUR
        Expenses:Food:Drinks      1.80 EUR
          shared: "Assets:Debtors:Bob 4.00 EUR"
          shared901: "Assets:Debtors:Charlie 40% (2.40 EUR)"
          shared902: "Assets:Debtors:David (30%, 1.80 EUR)"
        Assets:Debtors:Bob        4.00 EUR
          shared: "Expenses:Food:Drinks 4.00 EUR"
        Assets:Debtors:Charlie    2.40 EUR
          shared: "Expenses:Food:Drinks 40% (2.40 EUR)"
        Assets:Debtors:David      1.80 EUR
          shared: "Expenses:Food:Drinks (30%, 1.80 EUR)"

  Scenario: Share a posting to the same account several times using absolute amounts
    When this transaction is processed:
      2020-01-01 * "BarAlice" "Beer with my guy friends"
        Assets:Cash               -10.00 EUR
        Expenses:Food:Drinks
          share: "Bob-4"
          share2: "Bob-4"

    Then should not error
    Then the original transaction should be modified:
      2020-01-01 * "BarAlice" "Beer with my guy friends"
        Assets:Cash           -10.00 EUR
        Expenses:Food:Drinks    2.00 EUR
          shared: "Assets:Debtors:Bob 4.00 EUR"
          shared901: "Assets:Debtors:Bob 4.00 EUR"
        Assets:Debtors:Bob      8.00 EUR
          shared: "Expenses:Food:Drinks 4.00 EUR"
          shared901: "Expenses:Food:Drinks 4.00 EUR"

  Scenario: Share a posting to the same account several times using relative amounts
    When this transaction is processed:
      2020-01-01 * "BarAlice" "Beer with my friend Bob (a lot)"
        Assets:Cash               -10.00 EUR
        Expenses:Food:Drinks
          share: "Bob-40%"
          share2: "Bob-40%"

    Then should not error
    Then the original transaction should be modified:
      2020-01-01 * "BarAlice" "Beer with my friend Bob (a lot)"
        Assets:Cash           -10.00 EUR
        Expenses:Food:Drinks    2.00 EUR
          shared: "Assets:Debtors:Bob 40% (4.00 EUR)"
          shared901: "Assets:Debtors:Bob 40% (4.00 EUR)"
        Assets:Debtors:Bob      8.00 EUR
          shared: "Expenses:Food:Drinks 40% (4.00 EUR)"
          shared901: "Expenses:Food:Drinks 40% (4.00 EUR)"

  Scenario: Share a posting to the same account several times using omitted amounts
    When this transaction is processed:
      2020-01-01 * "BarAlice" "Beer with my friend Bob (a lot)"
        Assets:Cash               -10.00 EUR
        Expenses:Food:Drinks
          share: "Bob"
          share2: "Bob"

    Then should not error
    Then the original transaction should be modified:
      2020-01-01 * "BarAlice" "Beer with my friend Bob (a lot)"
        Assets:Cash           -10.00 EUR
        Expenses:Food:Drinks    3.34 EUR
          shared: "Assets:Debtors:Bob (33%, 3.33 EUR)"
          shared901: "Assets:Debtors:Bob (33%, 3.33 EUR)"
        Assets:Debtors:Bob      6.66 EUR
          shared: "Expenses:Food:Drinks (33%, 3.33 EUR)"
          shared901: "Expenses:Food:Drinks (33%, 3.33 EUR)"

  Scenario: Share a posting to the same account several times using mixed amounts
    When this transaction is processed:
      2020-01-01 * "BarAlice" "Beer with my friend Bob (a lot)"
        Assets:Cash               -10.00 EUR
        Expenses:Food:Drinks
          share: "Bob-4"
          share2: "Bob-40%"
          share3: "Bob"

    Then should not error
    Then the original transaction should be modified:
      2020-01-01 * "BarAlice" "Beer with my friend Bob (a lot)"
        Assets:Cash           -10.00 EUR
        Expenses:Food:Drinks    1.80 EUR
          shared: "Assets:Debtors:Bob 4.00 EUR"
          shared901: "Assets:Debtors:Bob 40% (2.40 EUR)"
          shared902: "Assets:Debtors:Bob (30%, 1.80 EUR)"
        Assets:Debtors:Bob      8.20 EUR
          shared: "Expenses:Food:Drinks 4.00 EUR"
          shared901: "Expenses:Food:Drinks 40% (2.40 EUR)"
          shared902: "Expenses:Food:Drinks (30%, 1.80 EUR)"
