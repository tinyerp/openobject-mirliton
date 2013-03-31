# -*- coding: utf-8 -*-
import base64

from support import *


@step('I render the report "{report_name}"')
def impl(ctx, report_name):
    part = ctx.data['record']
    assert_equal(part._model_name, 'res.partner')
    rv = ctx.client.render_report(report_name, [part.id])
    ctx.data['report'] = rv
    assert_true(rv['state'])


@step('a PDF document is returned')
def impl(ctx):
    report = ctx.data['report']
    assert_equal(report['format'], 'pdf')
    content = base64.b64decode(report['result'])
    # Verify that the document quacks like a PDF
    assert_equal(content[:4], '%PDF')
    assert_equal(content[-5:], '%EOF\n')
