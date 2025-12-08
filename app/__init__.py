# /app/__init__.py

# Function that produces our Flask apps and returns Flask apps

from flask import Flask
from .extensions import ma, limiter, cache
from .models import db
from .blueprints.customers import customers_bp
from .blueprints.mechanics import mechanics_bp
from .blueprints.service_tickets import service_tickets_bp
from .blueprints.inventory import inventory_bp
import config
from flask_swagger_ui import get_swaggerui_blueprint
# from .routes.init_db import init_bp

SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI - to view the documentation
API_URL = '/static/swagger.yaml'  # Our API URL - grab our hosts the host URL from the swagger.yaml file

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Mechanic Shop API"
    }
)

def create_app(config_name='DevelopmentConfig'):
    app = Flask(__name__)
    app.config.from_object(getattr(config, config_name))
    
    # Initialize extensions
    ma.init_app(app)
    db.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)
    
    # IMPORTANT — prevent ResourceWarning from SQLite
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()
        try:
            db.engine.dispose()
        except:
            pass
    
    
    # Register blueprints 
    app.register_blueprint(customers_bp, url_prefix='/customers')
    app.register_blueprint(mechanics_bp, url_prefix='/mechanics')
    app.register_blueprint(service_tickets_bp, url_prefix='/service_tickets')
    app.register_blueprint(inventory_bp, url_prefix='/inventory')
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    # app.register_blueprint(init_bp)
    
    return app