Feature: Configure plugin behavior

  Scenario: Disable adding new meta

    Given this config:
      {"meta_name": None}

    When this transaction is processed:
      2020-01-01 * "BarAlice" "Lunch with friend Bob" #share-Bob
        Assets:Cash               -10.00 USD
        Expenses:Food:Drinks

    Then the original transaction should be modified:
      2020-01-01 * "BarAlice" "Lunch with friend Bob"
        Assets:Cash               -10.00 USD
        Expenses:Food:Drinks        5.00 USD
        Assets:Debtors:Bob          5.00 USD

  Scenario: Rename added meta

    Given this config:
      {"meta_name": 'asdf'}

    When this transaction is processed:
      2020-01-01 * "BarAlice" "Lunch with friend Bob" #share-Bob
        Assets:Cash               -10.00 USD
        Expenses:Food:Drinks

    Then the original transaction should be modified:
      2020-01-01 * "BarAlice" "Lunch with friend Bob"
        Assets:Cash               -10.00 USD
        Expenses:Food:Drinks        5.00 USD
          asdf: "Assets:Debtors:Bob (50%, 5.00 USD)"
        Assets:Debtors:Bob          5.00 USD
          asdf: "Expenses:Food:Drinks (50%, 5.00 USD)"
