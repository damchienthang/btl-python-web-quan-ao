from website import create_app
from website.models import User, Cart, CartItem, Product, Order

# Khởi tạo ứng dụng
app = create_app()

# Khởi tạo database
with app.app_context():
    User.init_db()
    Product.init_db()  # Thêm khởi tạo bảng products
    Cart.init_db()  # Thêm khởi tạo bảng carts
    CartItem.init_db()  # Giữ nguyên, nhưng phải sau Cart vì foreign key
    Order.init_db()

if __name__ == '__main__':
    app.run(debug=True)
