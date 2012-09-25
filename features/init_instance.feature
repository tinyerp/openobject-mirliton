# language: en

@init
Feature: Initialize a new database

  Automate the steps to install the database

  @newdb
  Scenario: Create a new database
    Given the server is on
    And database "behave" does not exist
    When we create a new database "behave"
    Then the database "behave" exists

  @newdb @login
  Scenario: Do login
    Given the database "behave" exists
    Then user "admin" log in with password "admin"

  @module_install
  Scenario: Install languages
    When we install the following languages:
      | lang  |
      | fr_FR |
      | de_DE |
      | it_IT |
    Then these languages should be available

  @module_install
  Scenario: Install modules
    When we install the required modules:
      | name                       |
      | base                       |
      | base_tools                 |
      | base_setup                 |
      | analytic                   |
      | board                      |
      | edi                        |
      | account_voucher            |
      | account_cancel             |
      | mail                       |
      | email_template             |
      | account_accountant         |
      | l10n_multilang             |
      | decimal_precision          |
      | account                    |
      | base_vat                   |
      | base_iban                  |
      | product                    |
      | stock                      |
      | process                    |
      | account_chart              |
      | account_payment            |
      | knowledge                  |
      | document                   |
    Then the modules are installed

  @setup
  Scenario: Stop scheduled tasks
    When we stop all scheduled tasks
    Then no task is scheduled

  @module_install
  Scenario: Update languages
    When we update the following languages:
      | lang  |
      | fr_FR |
      | de_DE |
      | it_IT |
    Then these languages should be available

  @module_install
  Scenario: Configure locales
    When we set these languages to swiss formatting:
      | lang  |
      | fr_FR |
      | de_DE |
      | it_IT |
      | en_US |
    Then all languages should be set to swiss formatting

  @setup
  Scenario: Set decimal precision
    When we set the "Account" decimal precision to 4 digits

  @setup
  Scenario: Create fiscal years
    When we create fiscal years since "2010"
    Then fiscal years are available

  @setup
  Scenario: Configure main partner and company
    When we need a "res.company" with xmlid "base.main_company"
      | name                   | value                         |
      | rml_header2            | 0                             |
      | rml_header1            | Acme AG                       |
      | rml_footer1            | service.center@acme.invalid   |
      | rml_footer2            | 0                             |
    # And its rml header is set to "resources/data/rml_header.txt"
    And the main company currency is "CHF" with a rate of "1.00"
    And we need a "res.partner" with xmlid "base.main_partner"
      | name                            | value                                  |
      | name                            | Acme                                   |
      | lang                            | fr_FR                                  |
      | website                         | www.acme.invalid                       |
      | customer                        | false                                  |
      | supplier                        | true                                   |
    And we need a "res.partner.address" with xmlid "base.main_address"
      | name       | value                       |
      | zip        | 1700                        |
      | fax        | 41016191010                 |
      | phone      | 41016191010                 |
      | email      | service.center@acme.invalid |
      | street     | Avenue de Beaulieu 10       |
      | street2    |                             |
      | city       | Fribourg                    |
      | name       | Acme                        |
      | country_id | by code: CH                 |

  @setup
  Scenario: Configure journal
    # Given an existing "account.journal" with name "Banque CHF" and type "bank"
    #   | name                      | value             |
    #   | default_debit_account_id  | by code: "190200" |
    #   | default_credit_account_id | by code: "190200" |
    Given all journals allow entry cancellation

  @setup
  Scenario: Configure bank account
    When we need a "res.partner.bank" with name "01-78067-7"
      | name             | value                       |
      | city             | Fribourg                    |
      | owner_name       | Acme                        |
      | name             | 01-78367-7                  |
      | zip              | 1700                        |
      | country_id       | by code: CH                 |
      | state            | bank                        |
      | street           | Avenue de Beaulieu 10       |
      | acc_number       | 01-78067-7                  |
      | partner_id       | by xmlid: base.main_partner |
      # | bank             | by code: Postfinance        |
