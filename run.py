from website import create_app
from website.models import User

# Khởi tạo ứng dụng
app = create_app()

# Khởi tạo database
with app.app_context():
    User.init_db()

if __name__ == '__main__':
    app.run(debug=True)
