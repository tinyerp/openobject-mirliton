# -*- coding: utf-8 -*-
from support import *
from support.openerp_helpers import (
    parse_domain, parse_table_values, build_search_domain,
    model_create, model_create_or_update)


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
