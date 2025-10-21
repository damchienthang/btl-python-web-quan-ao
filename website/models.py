from flask import current_app
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import os

class User:
    @staticmethod
    def get_db_connection():
        """Kết nối đến MySQL database"""
        try:
            conn = mysql.connector.connect(
                host='localhost',
                user='website_user',  # User bạn đã tạo
                password='Nhom16',  # Mật khẩu bạn đặt
                database='my_website',  # Database bạn đã tạo
                port=3306
            )
            return conn
        except mysql.connector.Error as e:
            print(f"Lỗi kết nối MySQL: {e}")
            return None

    @staticmethod
    def init_db():
        """Khởi tạo database và bảng users trong MySQL"""
        conn = User.get_db_connection()
        if conn is None:
            print("Không thể kết nối đến MySQL")
            return False
            
        cursor = conn.cursor()
        
        try:
            # Tạo bảng users
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    full_name VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            print("✅ Đã khởi tạo bảng users trong MySQL")
            return True
        except mysql.connector.Error as e:
            print(f"Lỗi khởi tạo database: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def create_user(username, email, password, full_name):
        """Tạo user mới trong MySQL"""
        conn = User.get_db_connection()
        if conn is None:
            return False
            
        cursor = conn.cursor()
        
        try:
            hashed_password = generate_password_hash(password)
            cursor.execute(
                'INSERT INTO users (username, email, password, full_name) VALUES (%s, %s, %s, %s)',
                (username, email, hashed_password, full_name)
            )
            conn.commit()
            return True
        except mysql.connector.IntegrityError:
            return False
        except mysql.connector.Error as e:
            print(f"Lỗi tạo user: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def verify_user(login_input, password):
        """Xác thực user bằng username HOẶC email trong MySQL"""
        conn = User.get_db_connection()
        if conn is None:
            return None
            
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute(
                'SELECT * FROM users WHERE username = %s OR email = %s',
                (login_input, login_input)
            )
            user = cursor.fetchone()
            
            if user and check_password_hash(user['password'], password):
                return {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'full_name': user['full_name']
                }
            return None
        except mysql.connector.Error as e:
            print(f"Lỗi xác thực user: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def user_exists(username='', email=''):
        """Kiểm tra user đã tồn tại chưa trong MySQL"""
        conn = User.get_db_connection()
        if conn is None:
            return False
            
        cursor = conn.cursor()
        
        try:
            if username and email:
                cursor.execute(
                    'SELECT id FROM users WHERE username = %s OR email = %s',
                    (username, email)
                )
            elif username:
                cursor.execute(
                    'SELECT id FROM users WHERE username = %s',
                    (username,)
                )
            elif email:
                cursor.execute(
                    'SELECT id FROM users WHERE email = %s',
                    (email,)
                )
            else:
                return False
            
            user = cursor.fetchone()
            return user is not None
        except mysql.connector.Error as e:
            print(f"Lỗi kiểm tra user: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def update_user(user_id, full_name, email):
        """Cập nhật thông tin user trong MySQL"""
        conn = User.get_db_connection()
        if conn is None:
            return False
            
        cursor = conn.cursor()
        
        try:
            # Kiểm tra email đã tồn tại chưa (trừ user hiện tại)
            cursor.execute(
                'SELECT id FROM users WHERE email = %s AND id != %s',
                (email, user_id)
            )
            if cursor.fetchone():
                return False
            
            cursor.execute(
                'UPDATE users SET full_name = %s, email = %s WHERE id = %s',
                (full_name, email, user_id)
            )
            conn.commit()
            return True
        except mysql.connector.IntegrityError:
            return False
        except mysql.connector.Error as e:
            print(f"Lỗi cập nhật user: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def change_password(user_id, new_password):
        """Đổi mật khẩu user trong MySQL"""
        conn = User.get_db_connection()
        if conn is None:
            return False
            
        cursor = conn.cursor()
        
        try:
            hashed_password = generate_password_hash(new_password)
            cursor.execute(
                'UPDATE users SET password = %s WHERE id = %s',
                (hashed_password, user_id)
            )
            conn.commit()
            return True
        except mysql.connector.Error as e:
            print(f"Lỗi đổi mật khẩu: {e}")
            return False
        finally:
            cursor.close()
            conn.close()


class Product:
    """Class quản lý sản phẩm"""
    @staticmethod
    def init_db():
        """Khởi tạo bảng products trong MySQL"""
        conn = User.get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    price DECIMAL(10,2) NOT NULL,
                    color VARCHAR(50),
                    image_url VARCHAR(255),
                    category_id INT,  -- Thêm trường này để liên kết với danh mục
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES categories(id)  -- Liên kết với bảng categories
                )
            ''')
            conn.commit()
            print("Đã khởi tạo bảng products trong MySQL (với category_id)")
            return True
        except mysql.connector.Error as e:
            print(f"Lỗi khởi tạo bảng products: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def get_all_products():
        """Lấy tất cả sản phẩm"""
        conn = User.get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute('SELECT * FROM products')
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def get_product_by_id(product_id):
        """Lấy sản phẩm bằng ID"""
        conn = User.get_db_connection()
        if conn is None:
            return None
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute('SELECT * FROM products WHERE id = %s', (product_id,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()
    @staticmethod
    def get_products_by_category(category_id):
        return Product.get_products_by_category_and_price(category_id)
        
    @staticmethod
    def get_products_by_category_and_price(category_id, min_price=None, max_price=None):
        """Lấy sản phẩm theo category VÀ giá"""
        conn = User.get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            query = 'SELECT * FROM products WHERE category_id = %s'
            params = [category_id]
            
            if min_price is not None:
                query += ' AND price >= %s'
                params.append(min_price)
            if max_price is not None:
                query += ' AND price <= %s'
                params.append(max_price)
            
            query += ' ORDER BY price ASC'
            cursor.execute(query, params)
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_products_by_price(min_price=None, max_price=None):
        """Lấy sản phẩm theo giá (không category)"""
        conn = User.get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            query = 'SELECT * FROM products'
            params = []
            where_clause = False
            
            if min_price is not None:
                query += ' WHERE price >= %s'
                params.append(min_price)
                where_clause = True
            if max_price is not None:
                if where_clause:
                    query += ' AND'
                else:
                    query += ' WHERE'
                query += ' price <= %s'
                params.append(max_price)
            
            query += ' ORDER BY price ASC'
            cursor.execute(query, params)
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

class CartItem:
    """Class quản lý item trong giỏ hàng"""
    @staticmethod
    def init_db():
        """Khởi tạo bảng cart_items trong MySQL"""
        conn = User.get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cart_items (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    cart_id INT NOT NULL,
                    product_id INT NOT NULL,
                    quantity INT NOT NULL DEFAULT 1,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (cart_id) REFERENCES carts(id),
                    FOREIGN KEY (product_id) REFERENCES products(id),
                    UNIQUE KEY unique_cart_item (cart_id, product_id)
                )
            ''')
            conn.commit()
            print("Đã khởi tạo bảng cart_items trong MySQL")
            return True
        except mysql.connector.Error as e:
            print(f"Lỗi khởi tạo bảng cart_items: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def add_to_cart(cart_id, product_id, quantity=1):
        """Thêm hoặc cập nhật sản phẩm vào giỏ hàng"""
        conn = User.get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT quantity FROM cart_items WHERE cart_id = %s AND product_id = %s', (cart_id, product_id))
            existing = cursor.fetchone()
            if existing:
                new_quantity = existing[0] + quantity
                cursor.execute('UPDATE cart_items SET quantity = %s WHERE cart_id = %s AND product_id = %s', (new_quantity, cart_id, product_id))
            else:
                cursor.execute('INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (%s, %s, %s)', (cart_id, product_id, quantity))
            conn.commit()
            return True
        except mysql.connector.Error as e:
            print(f"Lỗi thêm vào giỏ hàng: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def get_cart_items(cart_id):
        """Lấy tất cả CartItem của cart"""
        conn = User.get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute('SELECT * FROM cart_items WHERE cart_id = %s', (cart_id,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def remove_from_cart(cart_id, product_id):
        """Xóa CartItem"""
        conn = User.get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM cart_items WHERE cart_id = %s AND product_id = %s', (cart_id, product_id))
            conn.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as e:
            print(f"Lỗi xóa khỏi giỏ hàng: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def update_quantity(cart_id, product_id, quantity):
        """Cập nhật quantity của CartItem"""
        if quantity < 1:
            return CartItem.remove_from_cart(cart_id, product_id)
        conn = User.get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE cart_items SET quantity = %s WHERE cart_id = %s AND product_id = %s', (quantity, cart_id, product_id))
            conn.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as e:
            print(f"Lỗi cập nhật quantity: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    @staticmethod
    def clear_cart(user_id):
        """Xóa toàn bộ giỏ hàng của user"""
        conn = CartItem.get_db_connection()
        if conn is None:
            return False
        
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM cart_items WHERE user_id = %s', (user_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Lỗi xóa giỏ hàng: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    @staticmethod
    def get_cart_items_with_products(cart_id):
        """Lấy cart items kèm thông tin sản phẩm đầy đủ"""
        conn = User.get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute('''
                SELECT 
                    ci.id,
                    ci.cart_id,
                    ci.product_id,
                    ci.quantity,
                    p.name as product_name,
                    p.price,
                    p.color as product_color,
                    p.image_url,
                    (p.price * ci.quantity) as subtotal
                FROM cart_items ci
                JOIN products p ON ci.product_id = p.id
                WHERE ci.cart_id = %s
            ''', (cart_id,))
            return cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"Lỗi lấy cart items với products: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
class Cart:
    """Class quản lý giỏ hàng tổng thể"""
    
    @staticmethod
    def init_db():
        """Khởi tạo bảng carts trong MySQL"""
        conn = User.get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS carts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL UNIQUE,  # Mỗi user có một cart duy nhất
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            conn.commit()
            print("Đã khởi tạo bảng carts trong MySQL")
            return True
        except mysql.connector.Error as e:
            print(f"Lỗi khởi tạo bảng carts: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def get_or_create_cart(user_id):
        """Lấy hoặc tạo cart cho user"""
        conn = User.get_db_connection()
        if conn is None:
            return None
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute('SELECT id FROM carts WHERE user_id = %s', (user_id,))
            cart = cursor.fetchone()
            if cart:
                return cart['id']
            else:
                cursor.execute('INSERT INTO carts (user_id) VALUES (%s)', (user_id,))
                conn.commit()
                return cursor.lastrowid
        except mysql.connector.Error as e:
            print(f"Lỗi lấy/tạo cart: {e}")
            return None
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def get_cart_subtotal(cart_id):
        """Tính subtotal của cart"""
        conn = User.get_db_connection()
        if conn is None:
            return 0.0
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT SUM(p.price * ci.quantity) AS subtotal
                FROM cart_items ci
                JOIN products p ON ci.product_id = p.id
                WHERE ci.cart_id = %s
            ''', (cart_id,))
            result = cursor.fetchone()
            return float(result[0]) if result[0] is not None else 0.0
        except mysql.connector.Error as e:
            print(f"Lỗi tính subtotal: {e}")
            return 0.0
        finally:
            cursor.close()
            conn.close()


class Order:
    """Class quản lý đơn hàng"""
    
    @staticmethod
    def init_db():
        """Khởi tạo bảng orders và order_items trong MySQL"""
        conn = User.get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            # Bảng orders
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    order_number VARCHAR(50) UNIQUE NOT NULL,
                    total_amount DECIMAL(10,2) NOT NULL,
                    status VARCHAR(20) DEFAULT 'pending',
                    shipping_address TEXT,
                    customer_name VARCHAR(255),
                    customer_email VARCHAR(255),
                    customer_phone VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            
            # Bảng order_items
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS order_items (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    order_id INT NOT NULL,
                    product_id INT NOT NULL,
                    product_name VARCHAR(255) NOT NULL,
                    quantity INT NOT NULL,
                    price DECIMAL(10,2) NOT NULL,
                    subtotal DECIMAL(10,2) NOT NULL,
                    FOREIGN KEY (order_id) REFERENCES orders(id),
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )
            ''')
            conn.commit()
            print("✅ Đã khởi tạo bảng orders và order_items trong MySQL")
            return True
        except mysql.connector.Error as e:
            print(f"Lỗi khởi tạo bảng orders: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def create_order(user_id, cart_items, customer_info, total_amount):
        """Tạo đơn hàng mới"""
        conn = User.get_db_connection()
        if conn is None:
            return None
        cursor = conn.cursor()
        try:
            # Tạo order number duy nhất
            from datetime import datetime
            order_number = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}-{user_id}"
            
            # Lưu order chính
            cursor.execute('''
                INSERT INTO orders (user_id, order_number, total_amount, shipping_address, 
                                  customer_name, customer_email, customer_phone, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'confirmed')
            ''', (
                user_id, order_number, total_amount, 
                customer_info['shipping_address'],
                customer_info['customer_name'],
                customer_info['customer_email'], 
                customer_info['customer_phone']
            ))
            
            order_id = cursor.lastrowid
            
            # Lưu order items
            for item in cart_items:
                cursor.execute('''
                    INSERT INTO order_items (order_id, product_id, product_name, quantity, price, subtotal)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (
                    order_id, item['product_id'], item['product_name'],
                    item['quantity'], item['price'], item['subtotal']
                ))
            
            conn.commit()
            return order_id
            
        except mysql.connector.Error as e:
            print(f"Lỗi tạo order: {e}")
            conn.rollback()
            return None
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_orders_by_user(user_id):
        """Lấy tất cả đơn hàng của user"""
        conn = User.get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute('''
                SELECT * FROM orders 
                WHERE user_id = %s 
                ORDER BY created_at DESC
            ''', (user_id,))
            return cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"Lỗi lấy orders: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_order_with_items(order_id):
        """Lấy chi tiết đơn hàng với các sản phẩm"""
        conn = User.get_db_connection()
        if conn is None:
            return None
        cursor = conn.cursor(dictionary=True)
        try:
            # Lấy thông tin order chính
            cursor.execute('SELECT * FROM orders WHERE id = %s', (order_id,))
            order = cursor.fetchone()
            
            if not order:
                return None
            
            # Lấy các sản phẩm trong order
            cursor.execute('''
                SELECT oi.*, p.image_url 
                FROM order_items oi 
                LEFT JOIN products p ON oi.product_id = p.id 
                WHERE oi.order_id = %s
            ''', (order_id,))
            order_items = cursor.fetchall()
            
            order['items'] = order_items
            return order
            
        except mysql.connector.Error as e:
            print(f"Lỗi lấy order details: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

class Category:
    """Class quản lý danh mục sản phẩm"""
    
    @staticmethod
    def init_db():
        """Khởi tạo bảng categories trong MySQL"""
        conn = User.get_db_connection()  # Sử dụng kết nối từ User class
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL UNIQUE,  -- Tên danh mục (ví dụ: 'Shirts', 'Pants')
                    description TEXT,  -- Mô tả danh mục (optional)
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            print("Đã khởi tạo bảng categories trong MySQL")
            return True
        except mysql.connector.Error as e:
            print(f"Lỗi khởi tạo bảng categories: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def add_category(name, description=None):
        """Thêm danh mục mới"""
        conn = User.get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO categories (name, description) VALUES (%s, %s)',
                (name, description)
            )
            conn.commit()
            return True
        except mysql.connector.IntegrityError:
            print(f"Danh mục '{name}' đã tồn tại!")
            return False
        except mysql.connector.Error as e:
            print(f"Lỗi thêm danh mục: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def get_all_categories():
        """Lấy tất cả danh mục"""

        conn = User.get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute('SELECT * FROM categories ORDER BY name ASC')
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def get_category_by_id(category_id):
        """Lấy danh mục bằng ID"""

        conn = User.get_db_connection()
        if conn is None:
            return None
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute('SELECT * FROM categories WHERE id = %s', (category_id,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()
