import os
from flask import Flask
from flask_bcrypt import Bcrypt
from config import Config, StagingConfig, ProductionConfig
from routes.user_routes import user_api
from routes.recipe_routes import recipe_api
from routes.feed_routes import feed_api
from routes.comment_routes import comments_api
from repository import mongo, bcrypt, mail, jwt_manager
import firebase_admin
from gevent.pywsgi import WSGIServer

def create_app() -> Flask:
    app = Flask(__name__)

    # Setup Mongo URI
    if os.environ.get('environment') == 'production':
        app.config.from_object(ProductionConfig())
    elif os.environ.get('environment') == 'staging':
        app.config.from_object(StagingConfig())
    else:
        app.config.from_object(Config())


    # Register blueprints
    app.register_blueprint(user_api)
    app.register_blueprint(recipe_api)
    app.register_blueprint(feed_api)
    app.register_blueprint(comments_api)

    # Init app 
    mongo.init_app(app=app)    
    mail.init_app(app=app)
    bcrypt.init_app(app=app)
    jwt_manager.init_app(app=app)

    return app


if __name__ == '__main__':
    app = create_app()

    firebase_admin.initialize_app()

    if os.environ.get('environment') == 'production' or os.environ.get('environment') == 'staging':
        http_server = WSGIServer(('127.0.0.1', 5050), app)
        http_server.serve_forever()
    else:
        app.run(host='0.0.0.0', port=5050)  
