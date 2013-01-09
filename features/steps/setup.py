# -*- coding: utf-8 -*-
import base64
from getpass import getpass
from datetime import date, timedelta

from support import *

TEST_DATABASE = 'behave'


def init_auth(ctx, db_name, user_password=None):
    if not user_password:
        if ('admin', db_name) in ctx.conf['auth']:
            return ctx.conf['auth'][('admin', db_name)]
        user_password = getpass("Password for user 'admin': ") or 'admin'
    ctx.conf['auth'][('admin', db_name)] = user_password
    return user_password


def get_db_name(ctx, db_name=None):
    try:
        return ctx.conf['db_name']
    except KeyError:
        pass
    if not db_name:
        db_name = ctx.conf['server'].tools.config['db_name']
    ctx.conf['db_name'] = db_name
    init_auth(ctx, db_name, 'admin' if db_name == TEST_DATABASE else None)
    return db_name


@given('the server is on')
def impl(ctx):
    db = ctx.client.db
    assert_in('server', ctx.conf.keys())
    assert_equal(db.server_version(), '6.1')


@given('database "{db_name}" does not exist')
def impl(ctx, db_name):
    db = ctx.client.db
    assert_not_in('db_name', ctx.conf.keys())
    # XXX deletion should be a separate step
    if db_name in db.list():
        admin_passwd = ctx.conf['admin_passwd']
        db.drop(admin_passwd, db_name)
    assert_not_in(db_name, db.list())


def _create_db(ctx, db_name):
    client = ctx.client
    admin_passwd = ctx.conf['admin_passwd']
    demo, lang = False, 'en_US'
    # XXX this should raise an error if the database exists already
    assert_is_not_none(db_name)
    if db_name not in client.db.list():
        client.create_database(admin_passwd, db_name, demo, lang)
    init_auth(ctx, db_name, 'admin')

@when('I create a new database "{db_name}"')
def impl(ctx, db_name):
    db_name = get_db_name(ctx, db_name)
    _create_db(ctx, db_name)

@when('I create a new database based on the configuration file')
def impl(ctx):
    db_name = get_db_name(ctx)
    _create_db(ctx, db_name)

@step('the database "{db_name}" exists')
def impl(ctx, db_name):
    assert_in(db_name, ctx.client.db.list())
    ctx.conf['db_name'] = db_name
    init_auth(ctx, db_name)
    # puts('Hey, db exists!')

@step('the database of the configuration file exists')
def impl(ctx):
    assert_in(ctx.conf['db_name'], ctx.client.db.list())

@step('the database of the configuration file exists otherwise I create it')
def impl(ctx):
    assert_is_not_none(ctx.conf['db_name'])
    if ctx.conf['db_name'] not in ctx.client.db.list():
        ctx.execute_steps(u'''
        When I create a new database based on the configuration file
        ''')

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
    ctx.conf['auth'][(user, db_name)] = password


# ir.module.module

@when('I install the required modules')
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


@given('the module "{name}" is installed')
def impl(ctx, name):
    mod = model('ir.module.module').get([('name', '=', name)])
    assert_equal(mod.state, 'installed')


@then('the models are loaded')
def impl(ctx):
    for (name,) in ctx.table:
        assert_true(model(name), 'Model %r is not loaded' % name)
    assert_true(model('res.partner'))


# ir.cron

@when('I stop all scheduled tasks')
def impl(ctx):
    # Retry 3 times
    for idx in '123':
        tasks = model('ir.cron').browse(['active = True'])
        if tasks:
            try:
                tasks.write({'active': False})
            except Exception:
                continue
        break


@then('no task is scheduled')
def impl(ctx):
    tasks = model('ir.cron').browse(['active = True'])
    assert_false(tasks)


# res.lang

@when('I install the following languages')
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


@when('I update the following languages')
def impl(ctx):
    tlangs = model('res.lang').browse([('translatable', '=', True)])
    codes = set([lang for (lang,) in ctx.table])
    mods = model('ir.module.module').browse(['state = installed'])
    assert_true(codes)
    assert_less(codes, set(tlangs.code))
    mods.button_update_translations()


@when('I set these languages to swiss formatting')
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


# decimal.precision

@when('I set the "{name}" decimal precision to {digits:d} digits')
def impl(ctx, name, digits):
    prec = model('decimal.precision').get([('name', '=', name)])
    assert_true(prec)
    prec.digits = digits
    prec = model('decimal.precision').get([('name', '=', name)])
    assert_equal(prec.digits, digits)
    #set_trace()


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


@step('all taxes are in TTC mode')
def impl(ctx):
    taxes = model('account.tax').browse([])
    assert_true(taxes)
    taxes.write({'price_include': True})


# res.company

@step('its rml header is set to "{path}"')
def impl(ctx, path):
    company = ctx.data['record']
    with open(path) as f:
        header = f.read()
    company.write({
        'rml_header': header,
        'rml_header2': header,
    })


@step('the company has the "{path}" logo')
def impl(ctx, path):
    company = ctx.data['record']
    with open(path) as f:
        img = base64.b64encode(f.read())
    company.logo = img


@step('the main company currency is "{code}" with a rate of "{rate:f}"')
def impl(ctx, code, rate):
    company = ctx.data['record']
    curr = model('res.currency').get([('name', '=', code)])
    assert_true(curr)
    assert_true(curr.rate)
    curr.rate = rate
    company.currency_id = curr.id


# ir.translation

@step('the translation for "{src}" in "{name}", language "{lang}" is "{value}"')
def impl(ctx, src, name, lang, value):
    res = ctx.data['record']
    assert_true(res)
    trans_line = model('ir.translation').get([
        'src = %s' % src, 'name = %s' % name, 'type = model',
        'lang = %s' % lang, 'res_id = %s' % res.id])
    if not trans_line:
        trans_line = model('ir.translation').create({
            'src': src, 'name': name, 'type': 'model',
            'lang': lang, 'res_id': res.id})
    trans_line.value = value


# res.users

@step('there is no user with login "{login}"')
def impl(ctx, login):
    user = model('res.users').get(['login = %s' % login])
    if user:
        user.write({'active': False})
        user.unlink()


@step('I duplicate the user "{username}"')
def impl(ctx, username):
    tmpl_user = model('res.users').get(['name = %s' % username, 'active = False'])
    assert_true(tmpl_user)
    assert_true(ctx.table)
    defaults = dict([(attr, value) for (attr, value) in ctx.table])
    defaults['active'] = True
    new_user = tmpl_user.copy(defaults)
    assert_greater(new_user.id, 0)


# ir.header_webkit

@step('I link the report "{name}" to this webkit_header')
def impl(ctx, name):
    head = ctx.data['record']
    assert_true(head)
    report = model('ir.actions.report.xml').get(['name = %s' % name])
    assert_true(report)
    report.write({'webkit_header': head.id})
