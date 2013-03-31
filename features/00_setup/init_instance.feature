# language: en

@init
Feature: Initialize a new database
  In order to prepare a new instance
  As a system administrator
  I want to create a database and load the initial data

  @newdb
  Scenario: Create a new database
    Given the server is up and running OpenERP 6.1
    And database "behave" does not exist
    When I create a new database "behave"
    Then the database "behave" exists

  @newdb @login
  Scenario: Do login
    Given the database "behave" exists
    Then user "admin" log in with password "admin"

  @module_install
  Scenario: Install languages
    When I install the following languages:
      | lang  |
      | fr_FR |
      | de_DE |
      | it_IT |
    Then these languages should be available

  @module_install
  Scenario: Install modules
    When I install the required modules:
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
      | l10n_ch                    |
      | knowledge                  |
      | document                   |
      | sale                       |
      | report_webkit              |
    Then the modules are installed

  @setup
  Scenario: Stop scheduled tasks
    When I stop all scheduled tasks
    Then no task is scheduled

  @module_install
  Scenario: Update languages
    When I update the following languages:
      | lang  |
      | fr_FR |
      | de_DE |
      | it_IT |
    Then these languages should be available

  @module_install
  Scenario: Configure locales
    When I set these languages to swiss formatting:
      | lang  |
      | fr_FR |
      | de_DE |
      | it_IT |
      | en_US |
    Then all languages should be set to swiss formatting

  @setup
  Scenario: Configure WebKit
    When the webkit path is configured

  @setup
  Scenario: Set decimal precision
    When I set the "Account" decimal precision to 4 digits

  @setup
  Scenario: Generate account chart
    Given the module "account" is installed
    And no account is set
    When I generate account chart:
      | template               | digits |
      | Plan comptable STERCHI | 0      |
    Then accounts should be available

  @setup
  Scenario: Create fiscal years
    When I create fiscal years since "2012"
    Then fiscal years are available

  @setup
  Scenario: Configure main partner and company
    Given an existing "res.company" with xmlid "base.main_company"
      | name                   | value                         |
      | rml_header2            | 0                             |
      | rml_header1            | Acme AG                       |
      | rml_footer1            | service.center@acme.invalid   |
      | rml_footer2            | 0                             |
    And the company currency is "CHF" with a rate of "1.00"
    And there is an existing "res.partner" with xmlid "base.main_partner"
      | name                            | value            |
      | name                            | Acme             |
      | lang                            | fr_FR            |
      | website                         | www.acme.invalid |
      | customer                        | false            |
      | supplier                        | true             |
    And there is an existing "res.partner.address" with xmlid "base.main_address"
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
    Given an existing "account.journal" with name "Banque CHF" and type "bank"
      | name                      | value             |
      | default_debit_account_id  | by code: "190200" |
      | default_credit_account_id | by code: "190200" |
    Given all journals allow entry cancellation

  @setup
  Scenario: Configure bank account
    Given a new or existing "res.partner.bank" with name "01-78067-7"
      | name             | value                       |
      | city             | Fribourg                    |
      | owner_name       | Acme                        |
      | name             | 01-78067-7                  |
      | zip              | 1700                        |
      | country_id       | by code: CH                 |
      | state            | bank                        |
      | street           | Avenue de Beaulieu 10       |
      | acc_number       | 01-78067-7                  |
      | partner_id       | by xmlid: base.main_partner |
