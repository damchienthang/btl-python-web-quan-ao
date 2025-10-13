# website/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

# Khởi tạo đối tượng SQLAlchemy để tương tác với CSDL
db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    """
    Hàm khởi tạo và cấu hình ứng dụng Flask.
    """
    app = Flask(__name__)
    
    # Cấu hình khóa bí mật để bảo vệ session
    app.config['SECRET_KEY'] = 'your_secret_key_here' 
    
    # Cấu hình đường dẫn đến file CSDL SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    
    # Liên kết đối tượng SQLAlchemy với ứng dụng Flask
    db.init_app(app)

    # Import các Blueprint
    from .views import views
    from .auth import auth

    # Đăng ký Blueprint với ứng dụng
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    # Import các model trước khi tạo CSDL
    from .models import User, Product, CartItem, Order, OrderItem

    # Tạo file CSDL nếu chưa tồn tại
    create_database(app)

    # Cấu hình Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'  # Chuyển hướng đến trang login nếu người dùng chưa đăng nhập
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

def create_database(app):
    """
    Kiểm tra và tạo CSDL nếu nó chưa tồn tại.
    """
    if not path.exists('website/' + DB_NAME):
        with app.app_context():
            db.create_all()
            print('Created Database!')
