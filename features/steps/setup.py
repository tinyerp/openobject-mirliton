# -*- coding: utf-8 -*-
from datetime import date

from environment import *


@given('the server is on')
def impl(ctx):
    db = ctx.client.db
    assert_in('server', ctx.conf.keys())
    assert_equal(db.server_version(), '6.1')


@given('database "{db_name}" does not exist')
def impl(ctx, db_name):
    db = ctx.client.db
    # XXX deletion should be a separate step
    assert_not_in('db_name', ctx.conf.keys())
    if db_name in db.list():
        admin_passwd = ctx.conf['admin_passwd']
        db.drop(admin_passwd, db_name)
    assert_not_in(db_name, db.list())


@when('we create a new database "{db_name}"')
def impl(ctx, db_name):
    client = ctx.client
    admin_passwd = ctx.conf['admin_passwd']
    demo, lang = False, 'en_US'
    # user_password = 'admin'
    # XXX this should raise an error if the database exists already
    if db_name not in client.db.list():
        client.create_database(admin_passwd, db_name, demo, lang)


@step('the database "{db_name}" exists')
def impl(ctx, db_name):
    assert_in(db_name, ctx.client.db.list())
    ctx.conf['db_name'] = db_name
    puts('Hey, db exists!')


@step('user "{user}" log in with password "{password}"')
def impl(ctx, user, password):
    client = ctx.client
    db_name = ctx.conf['db_name']
    uid = client.login(user, password, database=db_name)
    assert_equal(client.user, user)
    if user == 'admin':
        assert_equal(uid, 1)
    else:
        assert_greater(uid, 1)
    # set_trace()
    # assert_true(0)


@when('we install the following languages')
def impl(ctx):
    ctx.data['lang'] = cfglang = set()
    for (lang,) in ctx.table:
        if model('res.lang').search([('code', '=', lang)]):
            continue
        res = model('base.language.install').create({'lang': lang})
        model('base.language.install').lang_install([res.id])
        cfglang.add(lang)


@then('these languages should be available')
def impl(ctx):
    for lang in ctx.data['lang']:
        assert_true(model('res.lang').search([('code', '=', lang)]))


@when('we install the required modules')
def impl(ctx):
    client = ctx.client
    to_install = []
    to_upgrade = []
    installed_mods = client.modules(installed=True)['installed']
    for (mod,) in ctx.table:
        if mod in installed_mods:
            to_upgrade.append(mod)
        else:
            to_install.append(mod)
    client.upgrade(*to_upgrade)
    client.install(*to_install)
    ctx.data.setdefault('modules', set()).update(to_upgrade + to_install)


@then('the modules are installed')
def impl(ctx):
    client = ctx.client
    mods = client.modules(installed=True)
    assert_true(ctx.data['modules'])
    assert_less(ctx.data['modules'], set(mods['installed']))
    assert_equal(mods.keys(), ['installed'])
    # extra_modules = sorted(set(mods['installed']) - ctx.data['modules'])
    # assert_false(extra_modules)
    # 10 extra: web*


@then('the models are loaded')
def impl(ctx):
    for (name,) in ctx.table:
        assert_true(model(name), 'Model %r is not loaded' % name)
    assert_true(model('res.partner'))


@when('we stop all scheduled tasks')
def impl(ctx):
    tasks = model('ir.cron').browse(['active = True'])
    if tasks:
        tasks.write({'active': False})


@then('no task is scheduled')
def impl(ctx):
    tasks = model('ir.cron').browse(['active = True'])
    assert_false(tasks)


@when('we update the following languages')
def impl(ctx):
    tlangs = model('res.lang').browse([('translatable', '=', True)])
    codes = set([lang for (lang,) in ctx.table])
    mods = model('ir.module.module').browse(['state = installed'])
    assert_true(codes)
    assert_less(codes, set(tlangs.code))
    mods.button_update_translations()


@when('we set these languages to swiss formatting')
def impl(ctx):
    langs = [lang for (lang,) in ctx.table]
    langs = model('res.lang').browse([('code', 'in', langs)])
    assert_equal(len(langs), len(ctx.table.rows))
    langs.write({
        'date_format': '%d.%m.%Y',
        'decimal_point': '.',
        'thousands_sep': "'",
    })


@then('all languages should be set to swiss formatting')
def impl(ctx):
    langs = model('res.lang').search([('date_format != %d.%m.%Y')])
    assert_false(langs)


@when('we set the "{name}" decimal precision to {digits:d} digits')
def impl(ctx, name, digits):
    (prec,) = model('decimal.precision').browse([('name', '=', name)])
    assert_true(prec)
    prec.digits = digits
    (prec,) = model('decimal.precision').browse([('name', '=', name)])
    assert_equal(prec.digits, digits)
    #set_trace()


@given('the module "{name}" is installed')
def impl(ctx, name):
    (mod,) = model('ir.module.module').browse([('name', '=', name)])
    assert_equal(mod.state, 'installed')


@given('no account is set')
def impl(ctx):
    account_ids = model('account.account').search([], limit=1)
    # set_trace()
    assert_false(account_ids)


@then('accounts should be available')
def impl(ctx):
    account_ids = model('account.account').search([], limit=1)
    assert_true(account_ids)


@step('we create fiscal years since "{start_year:d}"')
def impl(ctx, start_year):
    stop_year = date.today().year
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


@step('its rml header is set to "{path}"')
def impl(ctx, path):
    company = ctx.data['record']
    with open(path) as f:
        header = f.read()
    company.write({
        'rml_header': header,
        'rml_header2': header,
    })


@step('the main company currency is "{code}" with a rate of "{rate:f}"')
def impl(ctx, code, rate):
    company = ctx.data['record']
    curr = model('res.currency').browse([('name', '=', code)])
    assert_true(curr)
    (curr,) = curr
    assert_true(curr.rate)
    curr.rate = rate
    company.currency_id = curr.id


@step('all journals allow entry cancellation')
def impl(ctx):
    journals = model('account.journal').browse([])
    assert_true(journals)
    journals.write({'update_posted': True})
