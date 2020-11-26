# -*- coding: utf-8 -*-

from flask_caching import Cache
from flask_executor import Executor
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# from flask_wtf.csrf import CSRFProtect

# csrf_protect = CSRFProtect()
# session_options={'autocommit': True}
db = SQLAlchemy(session_options={'autocommit': True})
migrate = Migrate()
cache = Cache(config={'CACHE_TYPE': 'simple'})
executor = Executor()
