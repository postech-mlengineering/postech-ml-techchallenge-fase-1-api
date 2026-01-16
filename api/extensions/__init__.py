from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
swagger = Swagger()
bcrypt = Bcrypt()
cache = Cache()
limiter = Limiter(
    key_func=get_remote_address, 
    default_limits=['60 per minute']
)