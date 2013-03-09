# -*- coding: utf-8 -*-
import ConfigParser as configparser

from support import tools
from support.tools import *

# ['model', 'puts', 'set_trace']    # + 20 'assert_*' helpers
__all__ = tools.__all__
OPENERP_ARGS = '-c etc/openerp-server.conf --without-demo all'
LOGFILE = 'var/log/behave-stdout.log'


def get_openerp_args(conf='erppeek.ini'):
    cp = configparser.SafeConfigParser()
    try:
        cp.read(conf)
        options = cp.get('DEFAULT', 'options')
    except configparser.Error:
        options = OPENERP_ARGS
    return '%s --logfile %s' % (options, LOGFILE)
