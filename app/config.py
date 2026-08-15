import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Base Configuration class."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-sahayak-super-secret')
    
    # SQLALCHEMY_TRACK_MODIFICATIONS = False is set elsewhere
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload configurations
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
    
    # CSRF Configuration
    WTF_CSRF_ENABLED = True

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        f"sqlite:///{os.path.join(BASE_DIR, 'sahayak.db')}"
    )

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    # In prod, we'll mandate a real database URL and strong secret key
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    @classmethod
    def init_app(cls, app):
        # Validate that configurations are set securely in production
        assert os.environ.get('SECRET_KEY'), "SECRET_KEY environment variable is required in production."
        assert os.environ.get('DATABASE_URL'), "DATABASE_URL environment variable is required in production."

config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
