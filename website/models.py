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
            print("Đã khởi tạo bảng users trong MySQL")
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

# Các class Product, CartItem, Order, OrderItem giữ nguyên...
# [Giữ nguyên phần code của các class này từ file cũ]

'''
Bạn thứ 2 bắt đầu làm từ đây
'''



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
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            print("Đã khởi tạo bảng products trong MySQL")
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


class Cart:
    """Class quản lý giỏ hàng"""
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
                    user_id INT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
    """Class quản lý đơn hàng - để phát triển sau"""
    @staticmethod
    def create_order(user_id, cart_items):
        """Tạo đơn hàng mới từ giỏ hàng - để phát triển sau"""
        return 1
    
    @staticmethod
    def get_user_orders(user_id):
        """Lấy đơn hàng của user - để phát triển sau"""
        return []

class OrderItem:
    """Class quản lý chi tiết đơn hàng - để phát triển sau"""
    @staticmethod
    def get_order_items(order_id):
        """Lấy chi tiết đơn hàng - để phát triển sau"""
        return []
