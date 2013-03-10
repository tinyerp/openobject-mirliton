# -*- coding: utf-8 -*-
from support import *
from support.openerp_helpers import (
    parse_domain, parse_table_values, build_search_domain,
    get_object, model_create, model_create_or_update)


def get_company_property(ctx, pname, modelname, fieldname, company_oid=None):
    company = None
    if company_oid:
        company = get_object(company_oid)
        assert_equal(company._model_name, 'res.company')
    field = model('ir.model.fields').get(
        [('name', '=', fieldname), ('model', '=', modelname)])
    assert_true(field, msg='no field %s in model %s' % (fieldname, modelname))

    values = {
        'name': pname,
        'fields_id': field.id,
        'res_id': False,
        'type': 'many2one',
    }
    if company:
        values['company_id'] = company.id
    return model_create_or_update(ctx, 'ir.property', values)


# Feature steps


@step(r'/^.*(?:need|there is|there\'s) (?:a|an|the) "([\w._]+)" with (.+)$/')
@step(r'/^.*(?:a|the) new or existing "([\w._]+)" with (.+)$/')
# Given a new or existing "res.partner" with name Isaac Newton
# Then I need a "res.partner" with name Isaac Newton
def impl(ctx, obj, domain):
    values = parse_domain(domain)
    new_values = ctx.table and parse_table_values(ctx, obj, ctx.table)
    ctx.data['record'] = model_create_or_update(ctx, obj, values, new_values)


@step(r'/^.*(?:an|the) existing "([\w._]+)" with (.+)$/')
# Given an existing "res.partner" with name Isaac Newton
def impl(ctx, obj, domain):
    values = parse_domain(domain)
    search_domain = build_search_domain(ctx, obj, values)
    assert_is_not_none(search_domain)
    record = model(obj).get(search_domain)
    assert_true(record)
    # Update existing record
    if ctx.table:
        values = parse_table_values(ctx, obj, ctx.table)
        record.write(values)
    ctx.data['record'] = record


@step(r'/^.*(?:a|the) new "([\w._]+)" with (.+)$/')
# Given a new "res.partner" with name Isaac Newton
def impl(ctx, obj, domain):
    values = parse_domain(domain)
    search_domain = build_search_domain(ctx, obj, values)
    found = search_domain and model(obj).get(search_domain)
    assert_false(found)
    # Create the record
    if ctx.table:
        values.update(parse_table_values(ctx, obj, ctx.table))
    ctx.data['record'] = model_create(ctx, obj, values)


@step(r'/^.*no "([\w._]+)" with (.+)$/')
# Given there's no "res.partner" with name Isaac Newton
def impl(ctx, obj, domain):
    values = parse_domain(domain)
    search_domain = build_search_domain(ctx, obj, values)
    record = search_domain and model(obj).get(search_domain)
    assert_false(record)


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
    assert_equal(len(ctx.data['records']), 1)
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


@given('I set global property named "{pname}" for model "{modelname}" and '
       'field "{fieldname}" for company with ref "{company_oid}"')
def impl(ctx, pname, modelname, fieldname, company_oid):
    ctx.data['record'] = get_company_property(ctx, pname, modelname, fieldname, company_oid=company_oid)


@given('I set global property named "{pname}" for model "{modelname}" and field "{fieldname}"')
def impl(ctx, pname, modelname, fieldname):
    ctx.data['record'] = get_company_property(ctx, pname, modelname, fieldname)


@step('the property is related to model "{modelname}" using column "{column}" and value "{value}"')
def impl(ctx, modelname, column, value):
    ir_property = ctx.data.get('record')
    assert_equal(ir_property._model_name, 'ir.property')
    res = model(modelname).get([(column, '=', value), ('company_id', '=', ir_property.company_id.id)])
    assert_true(res, msg="no record for %s = %r" % (column, value))
    ir_property.write({'value_reference': '%s,%s' % (modelname, res.id)})


@given('I am configuring the company with ref "{company_oid}"')
def impl(ctx, company_oid):
    c_domain = build_search_domain(ctx, 'res.company', {'xmlid': company_oid})
    company = model('res.company').get(c_domain)
    ctx.data['company_id'] = company.id
