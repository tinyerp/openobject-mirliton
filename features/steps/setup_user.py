# -*- coding: utf-8 -*-
import base64

from support import *


# res.users

@step('there is no user with login "{login}"')
def impl(ctx, login):
    user = model('res.users').get(['login = %s' % login])
    if user:
        user.write({'active': False})
        user.unlink()


@step('I duplicate the user "{username}"')
def impl(ctx, username):
    tmpl_user = model('res.users').get(['name = %s' % username, 'active = False'])
    assert_true(tmpl_user)
    assert_true(ctx.table)
    defaults = dict([(attr, value) for (attr, value) in ctx.table])
    defaults['active'] = True
    new_user = tmpl_user.copy(defaults)
    assert_greater(new_user.id, 0)
    ctx.data['record'] = new_user
