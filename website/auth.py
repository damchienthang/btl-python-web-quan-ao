
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from website.models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Xử lý đăng nhập"""
    # Nếu user đã đăng nhập, chuyển hướng đến dashboard
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        login_input = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        remember_me = request.form.get('remember-me')
        
        # Validation
        if not login_input:
            flash('Please enter your email!', 'error')
            return render_template('login.html')
        
        if not password:
            flash('Please enter your password!', 'error')
            return render_template('login.html')
        
        user = User.verify_user(login_input, password)
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['full_name'] = user['full_name']
            session['email'] = user['email']
            
            # Xử lý Remember Me
            if remember_me:
                session.permanent = True
            else:
                session.permanent = False
            
            flash('Login successful!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Email or password is incorrect!', 'error')
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Xử lý đăng ký"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        full_name = request.form.get('full_name', '').strip()
        agree_terms = request.form.get('agree_terms')
        
        # Kiểm tra các trường bắt buộc
        if not username:
            flash('Please enter username!', 'error')
            return render_template('register.html')
        
        if not email:
            flash('Please enter email!', 'error')
            return render_template('register.html')
        
        if not password:
            flash('Please enter password!', 'error')
            return render_template('register.html')
        
        if not confirm_password:
            flash('Please enter confirm password!', 'error')
            return render_template('register.html')
        
        # Kiểm tra định dạng email
        if '@' not in email or '.' not in email:
            flash('Invalid email format!', 'error')
            return render_template('register.html')
        
        # Kiểm tra điều khoản
        if not agree_terms:
            flash('You must agree with Privacy Policy and Terms of Use!', 'error')
            return render_template('register.html')
        
        # Kiểm tra mật khẩu xác nhận
        if password != confirm_password:
            flash('Passwords do not match! Please try again.', 'error')
            return render_template('register.html')
        
        # Kiểm tra độ dài mật khẩu
        if len(password) < 6:
            flash('Password must be at least 6 characters!', 'error')
            return render_template('register.html')
        
        # Kiểm tra định dạng full_name
        if full_name:
            import re

            name_pattern = r'^[a-zA-Z]+( [a-zA-Z]+)*$'
            if not re.match(name_pattern, full_name):
                flash('Full name can only contain letters (a-z, A-Z) and single spaces between words!', 'error')
                return render_template('register.html')
        
        # Kiểm tra độ dài username
        if len(username) < 3:
            flash('Username must be at least 3 characters!', 'error')
            return render_template('register.html')
        
        # Kiểm tra user đã tồn tại
        if User.user_exists(username, email):
            flash('Username or email already exists!', 'error')
            return render_template('register.html')
        
        # Tạo user mới
        if User.create_user(username, email, password, full_name):
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('CRegistration failed! Please try again.', 'error')
    
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    """Đăng xuất"""
    session.clear()
    flash('Logout successful! Have a good day,', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/forgot_password')
def forgot_password():
    """Xử lý quên mật khẩu - hiện thông báo ngay"""
    flash('Password reset feature will be available soon!', 'info')
    return redirect(url_for('auth.login'))

# API endpoints cho AJAX
@auth_bp.route('/api/check_username')
def check_username():
    """API kiểm tra username đã tồn tại chưa"""
    username = request.args.get('username', '').strip()
    if not username:
        return jsonify({'exists': False})
    
    exists = User.user_exists(username=username)
    return jsonify({'exists': exists})

@auth_bp.route('/api/check_email')
def check_email():
    """API kiểm tra email đã tồn tại chưa"""
    email = request.args.get('email', '').strip()
    if not email:
        return jsonify({'exists': False})
    
    exists = User.user_exists(email=email)
    return jsonify({'exists': exists})

@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    """API đổi mật khẩu"""
    # Kiểm tra user đã đăng nhập chưa
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'})
    
    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    user_id = session['user_id']
    
    # Validation
    if not old_password or not new_password:
        return jsonify({'success': False, 'message': 'Please fill in all fields'})
    
    if len(new_password) < 6:
        return jsonify({'success': False, 'message': 'New password must be at least 6 characters'})
    
    # Lấy thông tin user để kiểm tra mật khẩu cũ
    user = User.verify_user(session.get('email', ''), old_password)
    if not user:
        return jsonify({'success': False, 'message': 'Current password is incorrect'})
    
    # Đổi mật khẩu mới
    if User.change_password(user_id, new_password):
        return jsonify({'success': True, 'message': 'Password updated successfully'})
    else:
        return jsonify({'success': False, 'message': 'Failed to update password'})
