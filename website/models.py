from flask import current_app
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

class User:
    @staticmethod
    def init_db():
        """Khởi tạo database và bảng users"""
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                full_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()

    @staticmethod
    def get_db_connection():
        """Kết nối đến database"""
        conn = sqlite3.connect('users.db')
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def create_user(username, email, password, full_name):
        """Tạo user mới"""
        conn = User.get_db_connection()
        cursor = conn.cursor()
        
        try:
            hashed_password = generate_password_hash(password)
            cursor.execute(
                'INSERT INTO users (username, email, password, full_name) VALUES (?, ?, ?, ?)',
                (username, email, hashed_password, full_name)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    @staticmethod
    def verify_user(login_input, password):
        """Xác thực user bằng username HOẶC email"""
        conn = User.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT * FROM users WHERE username = ? OR email = ?',
            (login_input, login_input)
        )
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            return {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'full_name': user['full_name']
            }
        return None

    @staticmethod
    def user_exists(username='', email=''):
        """Kiểm tra user đã tồn tại chưa"""
        conn = User.get_db_connection()
        cursor = conn.cursor()
        
        if username and email:
            cursor.execute(
                'SELECT id FROM users WHERE username = ? OR email = ?',
                (username, email)
            )
        elif username:
            cursor.execute(
                'SELECT id FROM users WHERE username = ?',
                (username,)
            )
        elif email:
            cursor.execute(
                'SELECT id FROM users WHERE email = ?',
                (email,)
            )
        else:
            conn.close()
            return False
        
        user = cursor.fetchone()
        conn.close()
        
        return user is not None

    @staticmethod
    def update_user(user_id, full_name, email):
        """Cập nhật thông tin user"""
        conn = User.get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Kiểm tra email đã tồn tại chưa (trừ user hiện tại)
            cursor.execute(
                'SELECT id FROM users WHERE email = ? AND id != ?',
                (email, user_id)
            )
            if cursor.fetchone():
                return False
            
            cursor.execute(
                'UPDATE users SET full_name = ?, email = ? WHERE id = ?',
                (full_name, email, user_id)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    @staticmethod
    def change_password(user_id, new_password):
        """Đổi mật khẩu user"""
        conn = User.get_db_connection()
        cursor = conn.cursor()
        
        try:
            hashed_password = generate_password_hash(new_password)
            cursor.execute(
                'UPDATE users SET password = ? WHERE id = ?',
                (hashed_password, user_id)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error changing password: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def get_user_by_id(user_id):
        """Lấy thông tin user bằng ID"""
        conn = User.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'full_name': user['full_name']
            }
        return None
