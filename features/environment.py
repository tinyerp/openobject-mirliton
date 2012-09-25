# -*- coding: utf-8 -*-
import sys
import traceback
import ConfigParser as configparser

import erppeek


__all__ = ['model', 'puts', 'set_trace']    # + 20 'assert_*' helpers


def read_config(path='etc/openerp-server.conf'):
    """Extract settings from openerp configuration."""
    p = configparser.SafeConfigParser()
    with open(path) as f:
        p.readfp(f)
    host = p.get('options', 'xmlrpc_interface') or '127.0.0.1'
    port = p.get('options', 'xmlrpc_port') or '8069'
    admin_passwd = p.get('options', 'admin_passwd')
    return (host, port, admin_passwd)


def print_exc():
    """Print exception, and its relevant stack trace."""
    tb = sys.exc_info()[2]
    length = 0
    while tb and '__unittest' not in tb.tb_frame.f_globals:
        length += 1
        tb = tb.tb_next
    traceback.print_exc(limit=length)


def _patch_all():
    from behave import matchers
    # Print readable 'Fault' errors
    if traceback.format_exception.__module__ == 'traceback':
        traceback.__format_exception = traceback.format_exception
        traceback.format_exception = erppeek.format_exception

    # Detect the regex expressions
    # https://github.com/jeamland/behave/issues/73
    def get_matcher(func, string):
        if string[:1] == string[-1:] == '/':
            return matchers.RegexMatcher(func, string[1:-1])
        return matchers.current_matcher(func, string)
    matchers.get_matcher = get_matcher
_patch_all()


def before_all(ctx):
    (host, port, admin_passwd) = read_config()
    server = 'http://%s:%s' % (host, port)
    ctx._is_context = True
    ctx.client = erppeek.Client(server, verbose=ctx.config.verbose)
    ctx.conf = {
        'server': server,
        'admin_passwd': admin_passwd,
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
        set_trace()


# -------
# HELPERS
# -------

def _get_context(level=2):
    caller_frame = sys._getframe(level)
    while caller_frame:
        try:
            # Find the context in the caller's frame
            varname = caller_frame.f_code.co_varnames[0]
            ctx = caller_frame.f_locals[varname]
            if ctx._is_context:
                return ctx
        except Exception:
            pass
        # Go back in the stack
        caller_frame = caller_frame.f_back


def model(name):
    """Return an erppeek.Model instance."""
    ctx = _get_context()
    return ctx and ctx.client.model(name)


def puts(*args):
    """Print the arguments, after the step is finished."""
    ctx = _get_context()
    if ctx:
        # Append to the list of messages
        ctx._messages.extend(args)
    else:
        # Context not found
        for arg in args:
            print(arg)


# From 'nose.tools': https://github.com/nose-devs/nose/tree/master/nose/tools

def set_trace():
    """Call pdb.set_trace in the caller's frame.

    First restore sys.stdout and sys.stderr.  Note that the streams are
    NOT reset to whatever they were before the call once pdb is done!
    """
    import pdb
    for stream in 'stdout', 'stderr':
        output = getattr(sys, stream)
        orig_output = getattr(sys, '__%s__' % stream)
        if output != orig_output:
            # Flush the output before entering pdb
            if hasattr(output, 'getvalue'):
                orig_output.write(output.getvalue())
                orig_output.flush()
            setattr(sys, stream, orig_output)
    exc, tb = sys.exc_info()[1:]
    if tb:
        if isinstance(exc, AssertionError) and exc.args:
            # The traceback is not printed yet
            print_exc()
        pdb.post_mortem(tb)
    else:
        pdb.Pdb().set_trace(sys._getframe().f_back)


# Expose assert* from unittest.TestCase with pep8 style names
from unittest2 import TestCase
ut = type('unittest', (TestCase,), {'any': any})('any')
for oper in ('equal', 'not_equal', 'true', 'false', 'is', 'is_not', 'is_none',
             'is_not_none', 'in', 'not_in', 'is_instance', 'not_is_instance',
             'raises', 'almost_equal', 'not_almost_equal', 'sequence_equal',
             'greater', 'greater_equal', 'less', 'less_equal'):
    funcname = 'assert_' + oper
    globals()[funcname] = getattr(ut, 'assert' + oper.title().replace('_', ''))
    __all__.append(funcname)
del TestCase, ut, oper, funcname
