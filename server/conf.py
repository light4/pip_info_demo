# -*- coding: utf-8 -*-

import os
import sys

from oslo_config import cfg

from server import PROJECT_ROOT

CONF = cfg.CONF

myapp_opts = [
    cfg.StrOpt('title', default='Pip-Info', help='the app titile'),
    cfg.StrOpt('baseurl', default='', help='the app base url'),
    cfg.StrOpt('name', default='pip-info', help='the app name'),
    cfg.StrOpt('env', default='development', help='the app env (development, production, beta)'),
]

mail_opts = [
    cfg.StrOpt('from_addr', default='pipinfo@example.com', help='email from addr'),
    cfg.StrOpt('server', default='', help='mail server'),
    cfg.IntOpt('port', default=25, help='mail port')
]

CONF.register_opts(myapp_opts, 'myapp')
CONF.register_opts(mail_opts, 'mail')


# set config
def setup_conf(app_env='development', app_kind='web'):
    if "--" in sys.argv:
        args = sys.argv[sys.argv.index("--") + 1:]
    else:
        args = []

    common_config_file = os.path.join(PROJECT_ROOT, "etc/{}/common.conf".format(app_env))
    default_config_files = [common_config_file]
    app_config_file = os.path.join(PROJECT_ROOT, "etc/{}/{}.conf".format(app_env, app_kind))
    default_config_files.append(app_config_file)
    CONF(default_config_files=default_config_files, args=args)
    return CONF
