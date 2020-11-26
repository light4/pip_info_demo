# 前言

Python 在去哪儿 OpsDev 使用的比较广泛，如果没有特别的原因，多数项目都是用 Python 来写的。下面我们通过一个具体的例子，来看下一个 Python 项目在 OpsDev 的典型实施过程。

# 项目初始化

本次作为例子的是一个根据 Python 包名字查看其具体信息的项目，包括 web 界面和 api。

Python 管理依赖的工具相对其他语言来成熟度比较低。在 OpsDev 开始是用 `requirements.txt` 文件来管理的，开发和测试的依赖文件分别是 `dev-requirements.txt`，`test-requirements.txt`。不过随着最近 [poetry] 得到了越来越多的关注。我们也开始使用 [poetry] 来管理 Python 相关的项目。[poetry] 具体的使用方法请查看相关文档，[https://github.com/python-poetry/poetry][poetry]。
下边我们使用 [poetry] 来初始化项目:

```bash
poetry new pip_info
cd pip_info
# git 初始化项目并推送到代码仓库
```

# 项目后端

更新 `pyproject.toml` 文件，添加清华源，修改支持的 Python 版本，添加项目依赖。

```diff
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -4,11 +4,22 @@ version = "0.1.0"
description = ""
authors = ["lightning1141 <lightning1141@gmail.com>"]

+[[tool.poetry.source]]
+name = "tuna"
+url = "https://pypi.tuna.tsinghua.edu.cn/simple"
+default = true

+
[tool.poetry.dependencies]
-python = "^3.8"
+python = "^3.7"
+requests = "^2.24.0"

[tool.poetry.dev-dependencies]
-pytest = "^5.2"
+ipython = "^7.10"
+ipdb = "^0.12.3"
+isort = "^4.3"
+yapf = "^0.29.0"
+flake8 = "^3.7"
+pytest = "^5.4.3"
```

然后打包安装，测试项目没有问题

```bash
poetry update
poetry install
```

现在应该多了个 `poetry.lock` 文件，这个是 [poetry] 根据 `pyproject.toml` 依赖生成的，最好推送到代码仓库，这样打包发布时不会因为依赖不一致导致的各种问题。

## 更新实现

在 `pip_info` 目录下添加 `console.py` 并更新代码逻辑，然后添加 `scripts` 到 `pyproject.toml`，具体代码逻辑见 [https://github.com/light4/pip_info_demo/blob/main/server/apps/scripts/console.py][pip_info_demo_console]，下边是 `pyproject.toml` 的 diff。

```diff
diff --git a/pyproject.toml b/pyproject.toml
index 7c28282..6325c50 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -21,6 +21,9 @@ yapf = "^0.29.0"
flake8 = "^3.7"
pytest = "^5.4.3"

+[tool.poetry.scripts]
+pip-info = "pip_info.console:main"
```

## 更新项目结构

为了同时支持 web、api 和脚本，更新项目结构如下。
apps 下边包含 web、api 和 scripts 目录。libs 和 apps 同级，主要是为了存放各种支持库，比如说监控和发邮件之类的。services 下边是具体的逻辑实现

```plain
~/p/pip_info on  main [✘?] is 📦 v0.1.0 via 🐍 v3.8.6 🕙 19:41:21
❯ tree pip_info/
pip_info/
├── apps
│   ├── api
│   │   └── __init__.py
│   ├── __init__.py
│   ├── scripts
│   │   ├── console.py
│   │   └── __init__.py
│   └── web
│       └── __init__.py
├── __init__.py
├── libs
│   └── __init.py
└── services
    └── __init__.py
```

## 添加配置管理

OpsDev Python Web 项目几乎都是使用 `oslo-config` 管理配置的，同时使用 Supervisor 管理进程的起停。
经常变更的会存放在数据库，不经常变更的就存储在配置文件里了。配置一般分为开发、测试及线上三种环境，各环境配置包括通用配置、api 配置、web 配置和 supervisord 配置。
以下代码可以到 [`https://github.com/light4/pip_info_demo`][pip_info_demo] 查看

```bash
poetry add oslo-config
```

更新配置文件，包括各个环境的和 supervisord 的。

```plain
~/p/pip_info on  main [+] is 📦 v0.1.0 via 🐍 v3.8.6 🕙 20:12:34
❯ tree etc/
etc/
├── beta
│   ├── api.conf
│   ├── common.conf
│   ├── supervisor-pip_info.conf
│   └── web.conf
├── development
│   ├── api.conf
│   ├── common.conf
│   ├── supervisor-pip_info.conf
│   └── web.conf
└── production
    ├── api.conf
    ├── common.conf
    ├── supervisor-pip_info.conf
    └── web.conf
```

下边是线上环境的一些配置
`etc/common.conf`

```ini
[web]
bind=0.0.0.0
run_mode=gunicorn

[myapp]
env=prod
baseurl=http://pipinfo.example.com

[mail]
from_addr = pipinfo@example.com
server = mailserver.example.com
port = 25
```

`etc/supervisor-pip_info.conf`

```ini
[group:pip-info]
programs=pip-info-web,pip-info-api

[program:pip-info-web]
directory=/home/q/pip_info
command=env APP_ENV=prod /home/q/pip_info/.venv/gunicorn -w 10 -b :8000 server.apps.web:app
autostart=False         ;; 是否开机自动启动
autorestart=False       ;; 是否挂了自动重启
redirect_stderr=True    ;; 是否把 stderr 定向到 stdout
stopasgroup=True

[program:pip-info-api]
directory=/home/q/pip_info
command=env APP_ENV=prod /home/q/pip_info/.venv/gunicorn -w 10 -b :8001 server.apps.api:app
autostart=False         ;; 是否开机自动启动
autorestart=False       ;; 是否挂了自动重启
redirect_stderr=True    ;; 是否把 stderr 定向到 stdout
stopasgroup=True
```

首先将 pip_info 重命名为 server，这样更通用。
然后添加解析配置代码。

```python
# server/__init__.py
import os

PROJECT_ROOT = os.path.abspath(".")
```

```python
# server/conf.py
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
```

注意 `setup_conf`，这里可以应用可以根据变量 `app_env` 和 `app_kind` 自动找到对应的配置文件。Flask-App 里会用到。

## 添加 App

主要代码如下，详细代码可以到 [`https://github.com/light4/pip_info_demo`][pip_info_demo] 查看

```python
def create_app(app_env='production'):
    # set config
    CONF = setup_conf(app_env=app_env, app_kind='web')
    # setup_log(prefix="pip_info_web")

    # instantiate the app
    app = Flask(__name__)

    app.secret_key = CONF.myapp.secret_key
    app.permanent_session_lifetime = timedelta(days=15)

    register_extensions(app, CONF)
    register_blueprints(app)
    register_errorhandlers(app)

    return app


app_env = os.getenv('APP_ENV', 'production')
app = create_app(app_env)


def entry():
    app.run()
```

主要就是初始化配置，设置日志，设置插件以及蓝图。
app_env 从 `APP_ENV` 环境变量读取。entry 主要是为了生成脚本，这样可以用脚本启动程序。

## 添加并注册插件

```python
# server/extensions.py
from flask_caching import Cache
from flask_executor import Executor
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy(session_options={'autocommit': True})
migrate = Migrate()
cache = Cache(config={'CACHE_TYPE': 'simple'})
executor = Executor()
```

```python
# server/apps/api/__init__.py
# server/apps/web/__init__.py
def register_extensions(app, CONF):
    """Register Flask extensions."""
    cache.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    sentry_sdk.init(dsn=CONF.sentry.dsn, integrations=[FlaskIntegration()])
    executor.init_app(app)
    if app_env == 'development':
        from flask_debugtoolbar import DebugToolbarExtension
        debug_toolbar = DebugToolbarExtension()
        debug_toolbar.init_app(app)
    return None
```

项目后端就大致设置完成了，虽然还有很多可以讲，不过就先到这里吧。以后可以讲讲其他一些代码，比如说邮件通知、监控、错误日志收集等等。

# 项目前端

项目前端一般使用 `Vue` + `Element` + `Yarn`，推荐一个后端 Admin 模板
[https://github.com/PanJiaChen/vue-admin-template][vue-admin-template]。
通过模板，可以快速搭建出可用的系统，并且项目结构挺好的，可以很容易的修改更新。
打包软件推荐使用 `Parcel` [https://parceljs.org/getting_started.html][parceljs]，Parcel 是 Web 应用打包工具，适用于经验不同的开发者。它利用多核处理提供了极快的速度，并且不需要任何配置。

# 总结

这样的项目结构，结构比较清晰，并且可以做快速变更，上手也很容易。并且可以做成项目模板，快速进行项目的开发迭代。如果有什么想和我聊的，可以 QTalk 联系 `chenyuan.ning` 或者邮件联系 `lightning1141#gmail.com`。也可以在 [https://github.com/light4/pip_info_demo][pip_info_demo] 提 `issue`。
这次就说这么多，下次可以具体讲讲 Web 开发中 Debug 相关的。

### 参考连接

poetry: [https://github.com/python-poetry/poetry][poetry]
pip_info: [https://github.com/light4/pip_info_demo][pip_info_demo]
vue-admin-template: [https://github.com/PanJiaChen/vue-admin-template][vue-admin-template]
parceljs: [https://parceljs.org/getting_started.html][parceljs]

---

[poetry]: https://github.com/python-poetry/poetry
[pip_info_demo]: https://github.com/light4/pip_info_demo
[pip_info_demo_console]: https://github.com/light4/pip_info_demo/blob/main/server/apps/scripts/console.py
[vue-admin-template]: https://github.com/PanJiaChen/vue-admin-template
[parceljs]: https://parceljs.org/getting_started.html
