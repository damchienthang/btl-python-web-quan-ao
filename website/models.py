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
    """Class quản lý sản phẩm - để phát triển sau"""
    @staticmethod
    def init_db():
        """Khởi tạo database cho products - để phát triển sau"""
        pass
    
    @staticmethod
    def get_all_products():
        """Lấy tất cả sản phẩm - để phát triển sau"""
        return []
    
    @staticmethod
    def get_product_by_id(product_id):
        """Lấy sản phẩm bằng ID - để phát triển sau"""
        return None

class CartItem:
    """Class quản lý giỏ hàng - để phát triển sau"""
    @staticmethod
    def add_to_cart(user_id, product_id, quantity=1):
        """Thêm sản phẩm vào giỏ hàng - để phát triển sau"""
        return True
    
    @staticmethod
    def get_cart_items(user_id):
        """Lấy tất cả sản phẩm trong giỏ hàng - để phát triển sau"""
        return []
    
    @staticmethod
    def remove_from_cart(user_id, product_id):
        """Xóa sản phẩm khỏi giỏ hàng - để phát triển sau"""
        return True

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
