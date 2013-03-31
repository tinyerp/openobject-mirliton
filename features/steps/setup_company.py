# -*- coding: utf-8 -*-
import base64
import glob
import os.path

from support import *
from support.openerp_helpers import get_object, model_create_or_update


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


@step('the webkit path is configured')
def impl(ctx):
    # The binary is installed with a buildout recipe
    webkit_path = os.path.join('parts', 'wkhtmltopdf', 'wkhtmltopdf*')
    paths = glob.glob(webkit_path)
    param = model('ir.config_parameter').get(["key = webkit_path"])
    if not paths and param and param.value and os.path.exists(param.value):
        # If the path is correctly configured, this step is optional
        return
    assert_equal(len(paths), 1)
    webkit_path = os.path.realpath(paths[0])
    if param:
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


# ir.property

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
    company = get_object(company_oid)
    assert_equal(company._model_name, 'res.company')
    ctx.data['company_id'] = company.id
