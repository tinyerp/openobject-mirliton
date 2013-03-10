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


# smtplib mock

@step('no e-mail is sent')
def impl(ctx):
    assert_false(ctx.mock_smtp.sendmail.called)


@step('{count:d} e-mails are sent')
def impl(ctx, count):
    assert_equal(ctx.mock_smtp.sendmail.call_count, count)
    ctx.mock_smtp.reset_mock()


@step('an e-mail is sent from "{smtp_from}" to "{smtp_to}"')
def impl(ctx, smtp_from, smtp_to):
    # Check both the 'From:' and the 'To:' of the e-mail.
    # The arguments are regular expressions.
    #
    # In addition, if this step provides a docstring, check that
    # each line of the docstring is present in the message body.
    #  - If the docstring line has leading or trailing '...',
    #    the text is searched anywhere in the message body
    #  - Else, the docstring line should match exactly one
    #    of the message lines
    assert_equal(ctx.mock_smtp.sendmail.call_count, 1)
    args, kwargs = ctx.mock_smtp.sendmail.call_args
    ctx.mock_smtp.reset_mock()
    assert_false(kwargs)
    (arg_from, arg_to, arg_message) = args
    (arg_to,) = arg_to
    assert_true(re.match(smtp_from + '$', arg_from),
                msg="From address %r does not match %r" %
                (arg_from, smtp_from))
    assert_true(re.match(smtp_to + '$', arg_to),
                msg="To address %r does not match %r" %
                (arg_to, smtp_to))
    message = email.message_from_string(arg_message)
    assert_in(arg_from, message['From'])
    assert_in(arg_to, message['To'])
    if not ctx.text:
        return
    arg_message = arg_message.decode('utf-8')
    arg_lines = arg_message.splitlines()
    for line in ctx.text.splitlines():
        line = line.strip()
        if line.startswith('...') or line.endswith('...'):
            assert_in(line.strip('.'), arg_message)
        elif line:
            assert_in(line, arg_lines)
