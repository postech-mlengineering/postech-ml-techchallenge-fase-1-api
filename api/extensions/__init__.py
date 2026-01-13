from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_caching import Cache


db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
swagger = Swagger()
bcrypt = Bcrypt()
cache = Cache()