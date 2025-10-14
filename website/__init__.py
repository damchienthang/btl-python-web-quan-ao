from flask import Flask
from datetime import timedelta

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.secret_key = 'your-secret-key-change-in-production'
    app.permanent_session_lifetime = timedelta(days=30)
    
    # Import và đăng ký blueprints
    from website.auth import auth_bp
    from website.main import main_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    
    return app
