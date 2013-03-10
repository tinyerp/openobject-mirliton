# -*- coding: utf-8 -*-
import mock
import erppeek

from support import tools, behave_better
from support.mocks import mock_smtp_start, mock_ftp_start
from support.openerp_helpers import get_openerp_args

__all__ = []

# Print readable 'Fault' errors
tools.patch_traceback()
# Some monkey patches to enhance Behave
behave_better.patch_all()


def before_all(ctx):
    ctx._is_context = True
    openerp_args = get_openerp_args(erppeek.Client._config_file)
    server = erppeek.start_openerp_services(openerp_args)
    admin_passwd = server.tools.config['admin_passwd']
    ctx.client = erppeek.Client(server, verbose=ctx.config.verbose)
    ctx.conf = {
        'server': server,
        'admin_passwd': admin_passwd,
        'auth': {}
    }


def before_feature(ctx, feature):
    ctx.data = {}


def before_scenario(ctx, scenario):
    ctx.mock_smtp = mock_smtp_start()
    ctx.mock_ftp = mock_ftp_start()


def after_scenario(ctx, scenario):
    unexpected_call = False
    if ctx.mock_smtp.sendmail.called:
        # The e-mails should be acknowledged with the relevant Gherkin
        # sentence, for example "Then 3 e-mails are sent"
        unexpected_call = True
        for (args, _) in ctx.mock_smtp.sendmail.call_args_list:
            ctx.config.output.write(u'      Mail from "%s" to "%s"\n' %
                                    (args[0], u','.join(args[1])))
    if unexpected_call and ctx.config.stop:
        tools.set_trace()
    mock.patch.stopall()


def before_step(ctx, step):
    ctx._messages = []
    # Extra cleanup (should be fixed upstream?)
    ctx.table = None
    ctx.text = None


def after_step(ctx, laststep):
    if ctx._messages:
        # Flush the messages collected with puts(...)
        output = ctx.config.output
        for item in ctx._messages:
            for line in str(item).splitlines():
                output.write(u'      %s\n' % (line,))
        output.flush()
    if laststep.status == 'failed' and ctx.config.stop:
        # Enter the interactive debugger
        tools.set_trace()
