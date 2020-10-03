Feature: Share expenses with other people easily

    Scenario: Blais example in the docs

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
