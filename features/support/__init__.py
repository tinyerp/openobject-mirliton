# -*- coding: utf-8 -*-
import ConfigParser as configparser

from support import tools
from support.tools import *

# ['model', 'puts', 'set_trace']    # + 20 'assert_*' helpers
__all__ = tools.__all__


def read_config(path='etc/openerp-server.conf'):
    """Extract settings from openerp configuration."""
    p = configparser.SafeConfigParser()
    with open(path) as f:
        p.readfp(f)
    host = p.get('options', 'xmlrpc_interface') or '127.0.0.1'
    port = p.get('options', 'xmlrpc_port') or '8069'
    admin_passwd = p.get('options', 'admin_passwd')
    database = p.get('options', 'database')
    return (host, port, admin_passwd, database)
