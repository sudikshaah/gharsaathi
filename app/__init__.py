import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app.config import config_by_name

from flask_wtf.csrf import CSRFProtect

# Initialize Flask extensions
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'warning'
csrf = CSRFProtect()

def create_app(config_name='development'):
    """Flask Application Factory."""
    app = Flask(__name__)
    
    # Load configuration
    config_obj = config_by_name.get(config_name, config_by_name['default'])
    app.config.from_object(config_obj)
    
    # Custom prod initialization if applicable
    if hasattr(config_obj, 'init_app'):
        config_obj.init_app(app)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Register Blueprints
    from app.views.public import public_bp
    from app.views.auth import auth_bp
    from app.views.employer import employer_bp
    from app.views.helper import helper_bp
    from app.views.admin import admin_bp
    from app.views.api import api_bp

    app.register_blueprint(public_bp, url_prefix='/')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(employer_bp, url_prefix='/employer')
    app.register_blueprint(helper_bp, url_prefix='/helper')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')

    # Flask-Login user loader
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))

    return app
