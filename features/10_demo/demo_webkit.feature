# language: en

@demo
Feature: Demonstrate the WebKit report

  In order to demonstrate some features
  As an administrator
  I prepare and run some scenarii

  Background: the client is connected
    Given the user "admin" is connected

  Scenario: Install module "sale"
    When I install the required modules:
      | name |
      | sale |
    Then the module "sale" is installed
    And the models are loaded
      | name        |
      | res.partner |
      | sale.order  |

  Scenario: Generate a webkit report
    Given a new or existing "ir.actions.report.xml" with name Test WebKit
      | name               | value              |
      | report_type        | webkit             |
      | report_name        | test_webkit        |
      | model              | res.partner        |
      | report_webkit_data | Test WebKit Report |
    And a new or existing "res.partner" with name Very Big Corp.
    When I render the report "test_webkit"
    Then a PDF document is returned
