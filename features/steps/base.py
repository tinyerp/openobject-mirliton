# -*- coding: utf-8 -*-
from support import *


@step('it fails')
def impl(ctx):
    exception = ctx.data['exception']
    assert_true(exception)
    puts(exception)


@step('what')
@step('debug')
def impl(ctx):
    set_trace()
