Instructions
============

These instructions target a Debian Squeeze system.

Python 2.6 is required (2.7 is supported too).
It is recommended to work from a virtualenv (see below).


(0) Prerequisites
-----------------
::

 $ aptitude install virtualenvwrapper
 $ aptitude install python-dev libxml2-dev libxslt1-dev libpq-dev
 $ aptitude install libjpeg62-dev libldap2-dev libsasl2-dev libyaml-dev
 $ aptitude install bzr ghostscript graphviz postgresql-client
 $ mkdir ~/.virtualenvs

(Optionally) declare a shared location for installed eggs::

 $ mkdir -p ~/.buildout/eggs
 $ vim ~/.buildout/default.cfg

    [buildout]
    eggs-directory = <your_home_dir>/.buildout/eggs

Then logout and login (to activate the virtualenvwrapper scripts).


(0) Database setup
------------------
::

 $ aptitude install postgresql-9.1 postgresql-contrib-9.1
 $ sudo -u postgres createuser --login --createdb \
 >      --no-createrole --no-superuser --pwprompt openerp
 # Enter password 'openerp' for this user

If PostgreSQL is already installed on a separate server, adapt this step.


(1) Virtualenv setup
--------------------
::

 $ mkvirtualenv -p python2.6 --no-site-packages oe
 $ workon oe
 $ pip install -U pip distribute
 $ pip install Babel
 $ pip freeze


(2) OpenERP installation
------------------------
::

 $ git clone git://github.com/florentx/openobject-mirliton.git demo
 $ cd demo
 $ python bootstrap.py

 (verify and tweak the configuration, see instructions below)

 $ bin/buildout


(3) Run Tests
-------------
::

 $ bin/behave


(4) Run OpenERP
---------------
::

 $ bin/supervisord

 $ bin/supervisorctl status
 $ bin/supervisorctl help


Tweak the configuration
-----------------------

This is the content of the buildout:

- (README.rst, bootstrap.py)
- buildout.cfg                      (local conf)
- etc/buildout-base.cfg             (base conf for OpenERP)
- etc/buildout-pinned.cfg           (pin the required versions)
- etc/openerp-server.conf.default   (default server conf, unused)
- etc/openerp-server.conf.in        (template for server conf)

Preferably, put the local configuration in 'buildout.cfg'.
Then update and restart the server::

 $ bin/buildout
 $ bin/supervisorctl restart openerp

#
