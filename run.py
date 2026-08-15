import os
from app import create_app, db

# Create application instance
app = create_app(os.environ.get('FLASK_ENV', 'development'))

# Ensure database tables are created before launch
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    # Run Flask development server
    app.run(host='127.0.0.1', port=5000)
