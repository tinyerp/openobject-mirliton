Using Behave with OpenERP
=========================

Write features
--------------

Use the Gherkin syntax
 * http://packages.python.org/behave/tutorial.html
 * http://packages.python.org/behave/gherkin.html
 * https://github.com/cucumber/cucumber/wiki/Gherkin


Develop steps
-------------

Sample step implementation::

    @step('we verify that {a} + {b} = {result}')
    def impl(ctx, result, a, b):
        assert_equal(int(a) + int(b), int(result))

The default syntax for the step name is already quite powerful:
 * http://pypi.python.org/pypi/parse#format-syntax

The above example can be simplified with this syntax::

    @step('we verify that {a:d} + {b:d} = {result:d}')
    def impl(ctx, result, a, b):
        assert_equal(a + b, result)

The regex parser is used if the step name is enclosed between forward slashes.


These helpers are made available in the globals, thanks to the line
``from environment import *``:

* ``assert_equal(first, second, msg=None)``
* ``assert_not_equal(first, second, msg=None)``
* ``assert_true(expr, msg=None)``
* ``assert_false(expr, msg=None)``
* ``assert_is(first, second, msg=None)``
* ``assert_is_not(first, second, msg=None)``
* ``assert_is_none(expr, msg=None)``
* ``assert_is_not_none(expr, msg=None)``
* ``assert_in(first, second, msg=None)``
* ``assert_not_in(first, second, msg=None)``
* ``assert_is_instance(obj, cls, msg=None)``
* ``assert_not_is_instance(obj, cls, msg=None)``
* ``assert_raises(exception, callable, *args, **kwargs)``
* ``assert_raises(exception)`` --> used as a context manager


These checks are more specific:

* ``assert_almost_equal(first, second, places=7, msg=None, delta=None)``
* ``assert_not_almost_equal(first, second, places=7, msg=None, delta=None)``
* ``assert_greater(first, second, msg=None)``
* ``assert_greater_equal(first, second, msg=None)``
* ``assert_less(first, second, msg=None)``
* ``assert_less_equal(first, second, msg=None)``
* ``assert_sequence_equal(first, second, msg=None)``


These utilities help for the development of new steps:

* ``model(name)``  -- shortcut for ``ctx.client.model(name)``
* ``puts(*args)``  -- print the arguments after the step is done
* ``set_trace()``  -- drop immediately into the Python debugger


The first argument of the step definition is always the context ``ctx``.
This is the place to store information related to the tests.
It wears some handy intrinsic attributes in stacked layers:

(root)
 * ``ctx.failed``               -- global boolean
 * ``ctx.config``               -- behave configuration
(root, custom)
 * ``ctx.client``               -- connected ERPpeek client
 * ``ctx.conf``                 -- config dictionary

(feature layer)
 * ``ctx.feature``              -- Feature object
 * ``ctx.tags``                 -- set of tags
 * ``ctx.execute_steps(steps)`` -- execute steps (a multi-line string)
(feature, custom)
 * ``ctx.data``                 -- data dictionary in the Feature scope

(scenario layer)
 * ``ctx.scenario``             -- Scenario object
 * ``ctx.tags``                 -- set of tags
 * ``ctx.stdout_capture``       -- (optional) StringIO replacement for stdout
 * ``ctx.stderr_capture``       -- (optional) StringIO replacement for stderr
 * ``ctx.log_capture``          -- (optional) StringIO replacement for logging
 * ``ctx.active_outline``       -- active Row for the Scenario Outline

(step layer)
 * ``ctx.table``                -- Table associated with this step
 * ``ctx.text``                 -- multiline text associated with this step

More details:  `Behave documentation <http://packages.python.org/behave/>`_
