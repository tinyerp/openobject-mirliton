# language: en

@demo
Feature: Demonstrate some Gherkin sentences

  In order to demonstrate some features
  As an administrator
  I prepare and run some scenarii

  Background: the client is connected
    Given the user "admin" is connected

  Scenario: Select and try to delete the main company
    Given I need the "res.company" with xmlid base.main_company
    And there is a "res.company" with xmlid base.main_company
    And there's a "res.company" with xmlid base.main_company
    And no "res.company" with name World Company
    When I try to delete the main company
    Then it fails
    When I select all "res.company" with name World Company
    Then there is no record
    When I filter all "res.company" with xmlid base.main_company
    Then there is one record
    And there are some records
    When I select all the "res.company" with name World Company
    Then there is no record

  Scenario: Create, select and delete a partner
    Given a new or existing "res.partner" with name Very Big Corp.
    When I filter all "res.partner" with name Very Big Corp.
    Then there are some records
    When I delete all records
    And I filter all "res.partner" with name Very Big Corp.
    Then there is no record

  Scenario: Create, select and delete partner events
    When I create a new "res.partner.event" with name Easter
    And I create a new "res.partner.event" with name Whit Sunday
    And I search all "res.partner.event" with partner_id False
    Then there are some records
    And an existing "res.partner.event" with name Easter
    When I delete the record
    Then I find no "res.partner.event" with name Easter
    When I search all "res.partner.event" with partner_id False
    Then there are some records
    When I delete all records
    And I filter all "res.partner.event" with partner_id False
    Then there is no record

  Scenario: Update an attribute with the content of a file
    Given a new or existing "res.partner" with name Very Big Corp.
    When attribute "comment" is set from "features/environment.py"
    Then I execute the Python commands
    """
    part = ctx.data['record']
    part.refresh()
    assert_true(part.comment)
    assert_in('before_all', part.comment)
    """

  Scenario: Create a template, copy and delete users
    Given a new or existing "res.users" with name Short Lived Template and active False
      | name      | value             |
      | login     | short.lived.templ |
      | signature | short-lived-users |
    And no "res.users" with login short.lived.first
    When I duplicate the user "Short Lived Template"
      | name  | value             |
      | name  | Short Lived       |
      | login | short.lived.first |
    When I duplicate the user "Short Lived Template"
      | name  | value             |
      | name  | Short Lived Clone |
      | login | short.lived.clone |
    Then I filter all "res.users" with signature short-lived-users
    And there are some records
    And I delete all records
    Then I select the existing "res.users" with name Short Lived Template and active False
    And I delete the record

  Scenario: Execute SQL and Python commands
    Given there is a file "features/environment.py"
    When I execute the SQL commands
    """
    -- Two selects, only the result of the second one is saved
    -- in ctx.data['return']
    SELECT * FROM res_company;
    SELECT login FROM res_users;
    """
    Then I execute the Python commands
    """
    result = ctx.data['return']
    assert_true(result)

    # Check that 'admin' is in the result
    assert_in('admin', [login for (login,) in result])
    """
