from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


from . import books
from . import user
from . import users_access
from . import refresh_token_manager
from . import route_access_log
from . import book_recommendation