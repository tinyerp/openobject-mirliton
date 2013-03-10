# -*- coding: utf-8 -*-
import base64

from support import *


# res.company

@step('the company has the "{path}" logo')
def impl(ctx, path):
    company = ctx.data['record']
    with open(path) as image_file:
        encoded_image = base64.b64encode(image_file.read())
    company.write({'logo': encoded_image})


@step('the company currency is "{code}" with a rate of "{rate:f}"')
def impl(ctx, code, rate):
    company = ctx.data['record']
    currency_rate = model('res.currency.rate').get([('currency_id', '=', code)])
    assert_true(currency_rate)
    assert_true(currency_rate.currency_id)
    currency_rate.write({'rate': rate})
    company.write({'currency_id': currency_rate.currency_id.id})


@step('its rml header is set to "{path}"')
def impl(ctx, path):
    company = ctx.data['record']
    with open(path) as f:
        header = f.read()
    company.write({
        'rml_header': header,
        'rml_header2': header,
    })


@step('the webkit path is set to "{webkit_path}"')
def impl(ctx, webkit_path):
    param = model('ir.config_parameter').get(["key = webkit_path"])
    if key:
        param.write({'value': webkit_path})
    else:
        vals = {'key': 'webkit_path', 'value': webkit_path}
        model('ir.config_parameter').create(vals)


# ir.header_webkit

@step('I link the report "{name}" to this webkit_header')
def impl(ctx, name):
    head = ctx.data['record']
    assert_true(head)
    report = model('ir.actions.report.xml').get(['name = %s' % name])
    assert_true(report)
    report.write({'webkit_header': head.id})
