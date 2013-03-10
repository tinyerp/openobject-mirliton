# -*- coding: utf-8 -*-
from datetime import date, timedelta

from support import *


# account.account

@given('no account is set')
def impl(ctx):
    account_ids = model('account.account').search([], limit=1)
    # set_trace()
    assert_false(account_ids)


@when('I generate account chart')
def impl(ctx):
    for template, digits in ctx.table:
        chart = model('account.chart.template').get(
            [('name', '=', template)])
        assert_true(chart, "Can't find chart named %s" % template)
        existing = model('account.account').search(
            [('code', '=', chart.account_root_id.code)])
        if existing:
            # XXX remove?
            puts("Account chart %s already generated from %s" %
                 (chart.account_root_id.name, template))
        else:
            digits = int(digits)
            wmca = model('wizard.multi.charts.accounts')
            config_wizard = wmca.create(
                {'code_digits': digits, 'chart_template_id': chart.id})
            res = config_wizard.onchange_chart_template_id(chart.id, {})
            assert_in('value', res)
            config_wizard.write(res['value'])
            config_wizard.execute()
            # wmca.browse([config_wizard.id]).execute()
            puts("Chart of account generated ! ")


@then('accounts should be available')
def impl(ctx):
    account_ids = model('account.account').search([], limit=1)
    assert_true(account_ids)


@step('I create fiscal years since "{start_year:d}"')
def impl(ctx, start_year):
    stop_year = (date.today() + timedelta(days=90)).year
    assert_less_equal(start_year, stop_year)
    all_years = [str(yr) for yr in range(start_year, stop_year + 1)]
    ctx.data['fiscalyear'] = all_years
    for yr in all_years:
        if model('account.fiscalyear').search([('name', '=', yr)]):
            continue
        newfy = model('account.fiscalyear').create({
            'name': yr,
            'code': yr,
            'date_start': '%s-01-01' % yr,
            'date_stop': '%s-12-31' % yr,
        })
        model('account.fiscalyear').browse([newfy.id]).create_period()


@step('fiscal years are available')
def impl(ctx):
    all_years = ctx.data['fiscalyear']
    assert_true(all_years)
    fys = model('account.fiscalyear').search([('name', 'in', all_years)])
    assert_equal(len(fys), len(all_years))


@step('all journals allow entry cancellation')
def impl(ctx):
    journals = model('account.journal').browse([])
    assert_true(journals)
    journals.write({'update_posted': True})


@step('all prices are without taxes')
def impl(ctx):
    taxes = model('account.tax').browse([])
    assert_true(taxes)
    taxes.write({'price_include': False})
