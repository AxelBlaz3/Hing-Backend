from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_jwt_extended import JWTManager

mongo = PyMongo()
bcrypt = Bcrypt()
mail = Mail()
jwt_manager = JWTManager()