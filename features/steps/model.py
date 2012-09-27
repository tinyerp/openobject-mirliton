# -*- coding: utf-8 -*-
from ast import literal_eval
import time

from environment import *


def parse_domain(domain):
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
    return rv


def build_search_domain(ctx, obj, values):
    values = values.copy()
    xml_id = values.pop('xmlid', None)
    res_id = values.pop('id', None)
    if xml_id:
        module, name = xml_id.split('.')
        search_domain = [('module', '=', module), ('name', '=', name)]
        records = model('ir.model.data').browse(search_domain)
        if not records:
            return None
        res = records[0].read('model res_id')
        assert_equal(res['model'], obj)
        if res_id:
            assert_equal(res_id, res['res_id'])
        else:
            res_id = res['res_id']
    search_domain = [(key, '=', value) for (key, value) in values.items()]
    if res_id:
        search_domain = [('id', '=', res_id)] + search_domain
    return search_domain


def parse_table_values(ctx, obj, table):
    fields = model(obj).fields()
    assert_equal(len(table.headings), 2)
    assert_true(fields)
    res = {}
    for (key, value) in table:
        field_type = fields[key]['type']
        if field_type in ('char', 'text'):
            pass
        elif value.lower() in ('false', '0', 'no', 'f', 'n', 'nil'):
            value = False
        elif field_type in ('many2one', 'one2many', 'many2many'):
            relation = fields[key]['relation']
            if value.startswith('by '):
                values = parse_domain(value[3:])
                search_domain = build_search_domain(ctx, relation, values)
                if search_domain:
                    value = model(relation).browse(search_domain).id
                else:
                    value = []
            else:
                method = getattr(model(relation), value)
                value = method()
            if value and field_type == 'many2one':
                assert_equal(len(value), 1)
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


@step(r'/^.*(?:need|there is|there\'s) (?:a|an|the) "([\w._]+)" with (.+)$/')
@step(r'/^.*(?:a|the) new or existing "([\w._]+)" with (.+)$/')
# Given a new or existing "res.partner" with name Isaac Newton
# Then I need a "res.partner" with name Isaac Newton
def impl(ctx, obj, domain):
    values = parse_domain(domain)
    search_domain = build_search_domain(ctx, obj, values)
    found = search_domain and model(obj).browse(search_domain)
    if found:
        # Record already exists
        assert_equal(len(found), 1)
        record = found[0]
        if ctx.table:
            values = parse_table_values(ctx, obj, ctx.table)
            record.write(values)
    else:
        # Create the record
        xml_id = values.pop('xmlid', None)
        if ctx.table:
            values.update(parse_table_values(ctx, obj, ctx.table))
        assert_not_in('id', values)
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
    ctx.data['record'] = record


@step(r'/^.*(?:an|the) existing "([\w._]+)" with (.+)$/')
# Given an existing "res.partner" with name Isaac Newton
def impl(ctx, obj, domain):
    values = parse_domain(domain)
    search_domain = build_search_domain(ctx, obj, values)
    assert_is_not_none(search_domain)
    found = model(obj).browse(search_domain)
    assert_true(found)
    assert_equal(len(found), 1)
    record = found[0]
    if ctx.table:
        values = parse_table_values(ctx, obj, ctx.table)
        record.write(values)
    ctx.data['record'] = record


@step(r'/^.*(?:a|the) new "([\w._]+)" with (.+)$/')
# Given a new "res.partner" with name Isaac Newton
def impl(ctx, obj, domain):
    values = parse_domain(domain)
    search_domain = build_search_domain(ctx, obj, values)
    found = search_domain and model(obj).browse(search_domain)
    assert_false(found)
    # Create the record
    xml_id = values.pop('xmlid', None)
    if ctx.table:
        values.update(parse_table_values(ctx, obj, ctx.table))
    assert_not_in('id', values)
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
    ctx.data['record'] = record


@step(r'/^.*no "([\w._]+)" with (.+)$/')
# Given there's no "res.partner" with name Isaac Newton
def impl(ctx, obj, domain):
    values = parse_domain(domain)
    search_domain = build_search_domain(ctx, obj, values)
    records = search_domain and model(obj).browse(search_domain)
    assert_false(records)


@step(r'/^.*all (?:the )?"([\w._]+)" with (.+)$/')
# Given all "res.partner" with name Isaac Newton
def impl(ctx, obj, domain):
    values = parse_domain(domain)
    search_domain = build_search_domain(ctx, obj, values)
    assert_is_not_none(search_domain)
    records = model(obj).browse(search_domain)
    ctx.data['records'] = records


@step("there is no record")
def impl(ctx):
    assert_false(ctx.data['records'])


@step("there are some records")
def impl(ctx):
    assert_true(ctx.data['records'])


@step("there is one record")
def impl(ctx):
    assert_true(ctx.data['records'])
    assert_equal(len(ctx.data['records']))
    record = ctx.data['records'][0]
    assert_true(record)
    ctx.data['record'] = record


@step('attribute "{attr}" is set from "{path}"')
def impl(ctx, attr, path):
    record = ctx.data['record']
    assert_true(record)
    with open(path) as f:
        value = f.read()
    assert_true(value)
    record.write({attr: value})
