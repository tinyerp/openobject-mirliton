# -*- coding: utf-8 -*-
from support import *


@step('it fails')
def impl(ctx):
    exception = ctx.data['exception']
    assert_true(exception)
    puts(exception)


@step('what')
@step('debug')
def impl(ctx):
    set_trace()


# Generic data migration helpers

@step('I execute the Python commands')
def impl(ctx):
    assert_true(ctx.text)
    env = globals().copy()
    env['client'] = ctx.client
    exec ctx.text in env


@step('I execute the SQL commands')
def impl(ctx):
    # Multiple SQL commands are supported, separated by ';'
    # SQL comments are supported '-- '
    sql_commands = ctx.text.strip()
    assert_true(sql_commands)
    openerp = ctx.conf['server']
    db_name = ctx.conf['db_name']
    pool = openerp.modules.registry.RegistryManager.get(db_name)
    cr = pool.db.cursor()
    try:
        cr.autocommit(True)
        cr.execute(sql_commands)
        puts(cr.statusmessage)
        try:
            ctx.data['return'] = cr.fetchall()
        except Exception:
            # ProgrammingError: no results to fetch
            ctx.data['return'] = []
    finally:
        cr.close()


@step('there is a file "{path}"')
def impl(ctx, path):
    assert_true(os.path.isfile(path), msg="No such file: %r" % path)
    ctx.data['filepath'] = path
