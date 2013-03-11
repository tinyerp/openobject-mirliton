# -*- coding: utf-8 -*-
from ast import literal_eval
import ConfigParser as configparser
import time

from support.tools import *

__all__ = ['parse_domain', 'parse_table_values', 'build_search_domain',
           'get_object', 'model_create', 'model_create_or_update']

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


def parse_domain(domain):
    """Parse a text and return a dictionary for this domain."""
    rv = {}
    if domain[-1:] == ':':
        domain = domain[:-1]
    for term in domain.split(' and '):
        key, value = term.split(None, 1)
        if key[-1:] == ':':
            key = key[:-1]
        try:
            value = literal_eval(value)
        except Exception:
            # Interpret the value as a string
            pass
        rv[key.lstrip()] = value
    # Compatibility with old syntax (oid -> xmlid)
    if 'oid' in rv:
        assert 'xmlid' not in rv
        rv['xmlid'] = rv.pop('oid')
    return rv


def get_object(xml_id):
    """Return the record referenced by this xml_id."""
    module, name = xml_id.split('.')
    search_domain = [('module', '=', module), ('name', '=', name)]
    data = model('ir.model.data').read(search_domain, 'model res_id')
    if data:
        assert_equal(len(data), 1)
        return model(data[0]['model']).get(data[0]['res_id'])


def model_create(ctx, obj, values):
    """Create a new record with these values."""
    assert_not_in('id', values)
    xml_id = values.pop('xmlid', None)
    record = model(obj).create(values)
    assert_greater(record.id, 0)
    if xml_id:
        module, name = xml_id.split('.')
        imd = model('ir.model.data').create({
            'model': obj,
            'module': module,
            'name': name,
            'res_id': record.id,
        })
        assert_greater(imd.id, 0)
    return record


def model_create_or_update(ctx, obj, values, new_values=None):
    """Create or update a record with these values."""
    # Search existing record
    search_domain = build_search_domain(ctx, obj, values)
    record = search_domain and model(obj).get(search_domain)
    if record:
        # Record already exists
        if new_values:
            record.write(new_values)
    else:
        # Create the record
        if new_values:
            values.update(new_values)
        record = model_create(ctx, obj, values)
    return record


def build_search_domain(ctx, obj, values):
    """Prepare a search domain.

    The argument 'obj' is the name of the model.
    The argument 'values' is a dictionary {field_name: value}.
    """
    values = values.copy()
    xml_id = values.pop('xmlid', None)
    res_id = values.pop('id', None)
    if xml_id:
        record = get_object(xml_id)
        if not record:
            return None
        assert_equal(record._model_name, obj)
        if res_id:
            assert_equal(record.id, res_id)
        else:
            res_id = record.id
    search_domain = [(key, '=', value) for (key, value) in values.items()]
    if res_id:
        search_domain = [('id', '=', res_id)] + search_domain
    # support multi-company
    if 'company_id' in ctx.data and 'company_id' in model(obj).keys():
        search_domain.append(('company_id', '=', ctx.data['company_id']))
    return search_domain


def parse_table_values(ctx, obj, table, defaults=None):
    """Parse a table of (key, value) pairs.

    The argument 'obj' is the name of the model.
    The argument 'table' is an iterable of (key, value) pairs.
    The optional argument 'defaults' is a dict of default values.

    Each value is parsed according to the type of field.
    """
    fields = model(obj).fields()
    assert_true(fields)
    if hasattr(table, 'headings'):
        # if we have a real table, ensure it has 2 columns
        # otherwise, we will just fail during iteration
        assert_equal(len(table.headings), 2)
    if defaults:
        values = defaults.copy()
        values.update(table)
        res = values.copy()
        table = values.items()
    else:
        res = {}
    for (key, value) in table:
        if not isinstance(value, basestring):
            continue
        add_mode = False
        field_type = fields[key]['type']
        if field_type in ('char', 'text'):
            pass
        elif value.lower() in ('false', '0', 'no', 'f', 'n', 'nil'):
            value = False
        elif field_type in ('many2one', 'one2many', 'many2many'):
            relation = fields[key]['relation']
            add_mode = value.startswith('add all by ')
            if add_mode:
                value = value[4:]   # fall back on "all by xxx" below
            if value.startswith(('by ', 'all by ')):
                value = value.split('by ', 1)[1]
                values = parse_domain(value)
                search_domain = build_search_domain(ctx, relation, values)
                if search_domain:
                    value = model(relation).browse(search_domain).id
                else:
                    value = []
                if add_mode:
                    value = res.get(key, []) + value
            else:
                method = getattr(model(relation), value)
                value = method()
            if value and field_type == 'many2one':
                assert_equal(len(value), 1,
                             msg="more than one item found for %r" % key)
                value = value[0]
        elif field_type == 'integer':
            value = int(value)
        elif field_type == 'float':
            value = float(value)
        elif field_type == 'boolean':
            value = True
        elif field_type in ('date', 'datetime') and '%' in value:
            value = time.strftime(value)
        res[key] = value
    return res
