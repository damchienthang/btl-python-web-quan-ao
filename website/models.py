# website/models.py

from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

# Lớp User để quản lý người dùng
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    first_name = db.Column(db.String(150), nullable=False)
    cart_items = db.relationship('CartItem', backref='user', lazy=True)
    orders = db.relationship('Order', backref='user', lazy=True)

# Lớp Product để quản lý sản phẩm
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')

# Lớp CartItem để quản lý các món hàng trong giỏ hàng
class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    variant_id = db.Column(db.Integer, db.ForeignKey('product_variant.id'), nullable=False)
    variant = db.relationship('ProductVariant')

# Lớp Order để quản lý đơn hàng
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending')
    order_items = db.relationship('OrderItem', backref='order', lazy=True)

# Lớp OrderItem để quản lý chi tiết các sản phẩm trong một đơn hàng
class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False) # Lưu lại giá tại thời điểm mua
    product = db.relationship('Product')

# Lớp Category: Để phân loại sản phẩm
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    # Tạo mối quan hệ một-nhiều: Một Category có nhiều Product
    products = db.relationship('Product', backref='category', lazy=True)

# Sửa đổi Lớp Product để liên kết với Category
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    # Giá cơ sở, có thể được ghi đè bởi biến thể
    base_price = db.Column(db.Float, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    # Thêm ForeignKey để liên kết Product với Category
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    # Một Product có nhiều biến thể (ví dụ: áo màu đỏ size S, áo màu xanh size M)
    variants = db.relationship('ProductVariant', backref='product', lazy=True, cascade="all, delete-orphan")

# Lớp ProductVariant: Quản lý các phiên bản khác nhau của sản phẩm
class ProductVariant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Liên kết với sản phẩm "cha"
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    
    # Các thuộc tính đặc trưng của quần áo
    size = db.Column(db.String(20), nullable=False)  # Ví dụ: 'S', 'M', 'L', 'XL'
    color = db.Column(db.String(50), nullable=False) # Ví dụ: 'Trắng', 'Đen', 'Xanh Navy'
    
    # Giá có thể khác nhau cho từng biến thể (ví dụ: size XXL đắt hơn)
    price_override = db.Column(db.Float, nullable=True)
    
    # Thêm ràng buộc để mỗi cặp (sản phẩm, size, màu) là duy nhất
    __table_args__ = (db.UniqueConstraint('product_id', 'size', 'color', name='_product_size_color_uc'),)

    # Quan hệ một-một: Mỗi biến thể có một mục kho hàng tương ứng
    inventory = db.relationship('Inventory', backref='variant', uselist=False, cascade="all, delete-orphan")

# Lớp Inventory: Quản lý số lượng tồn kho
class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Liên kết một-một với một biến thể sản phẩm cụ thể
    variant_id = db.Column(db.Integer, db.ForeignKey('product_variant.id'), nullable=False, unique=True)
    quantity = db.Column(db.Integer, nullable=False, default=0) # Số lượng tồn kho

# Lớp Promotion (Khuyến mãi)
class Promotion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False) # Ví dụ: 'SALE20', 'FREESHIP'
    description = db.Column(db.String(255))
    discount_percentage = db.Column(db.Float, nullable=False) # % giảm giá
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)

# Lớp Shipment (Vận chuyển)
class Shipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    tracking_number = db.Column(db.String(100), unique=True) # Mã vận đơn
    carrier = db.Column(db.String(50)) # Hãng vận chuyển: 'GHTK', 'Viettel Post'
    shipped_date = db.Column(db.DateTime)
    delivered_date = db.Column(db.DateTime)
    status = db.Column(db.String(50), default='Preparing') # Ví dụ: 'Preparing', 'Shipped', 'Delivered', 'Cancelled'

    # Quan hệ một-một với Order
    order = db.relationship('Order', backref=db.backref('shipment', uselist=False))
