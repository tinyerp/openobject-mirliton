# -*- coding: utf-8 -*-
from getpass import getpass

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


@given('the server is up and running OpenERP {version}')
def impl(ctx, version):
    db = ctx.client.db
    assert_in('server', ctx.conf.keys())
    assert_equal(db.server_version(), version)


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


@step('the user "{user}" is connected')
def impl(ctx, user):
    client = ctx.client
    db_name = get_db_name(ctx, TEST_DATABASE)
    password = ctx.conf['auth'][(user, db_name)]
    uid = client.login(user, password, database=db_name)
    assert_equal(client.user, user)
    if user == 'admin':
        assert_equal(uid, 1)
    else:
        assert_greater(uid, 1)
