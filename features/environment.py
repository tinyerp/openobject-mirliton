# -*- coding: utf-8 -*-
import erppeek

from support import tools, behave_better, get_openerp_args

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
        # output.flush()
    if laststep.status == 'failed' and ctx.config.stop:
        # Enter the interactive debugger
        tools.set_trace()
