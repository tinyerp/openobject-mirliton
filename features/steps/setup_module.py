# -*- coding: utf-8 -*-
from support import *


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

@step('I install the following languages')
@step('I install the following language')
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


# decimal.precision

@when('I set the "{name}" decimal precision to {digits:d} digits')
def impl(ctx, name, digits):
    prec = model('decimal.precision').get([('name', '=', name)])
    assert_true(prec)
    prec.write({'digits': digits})
    prec.refresh()
    assert_equal(prec.digits, digits)
