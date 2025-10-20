from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from website.models import User, Cart, CartItem, Product
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Trang chủ - chuyển hướng đến đăng nhập"""
    return redirect(url_for('auth.login'))

@main_bp.route('/dashboard')
def dashboard():
    """Trang dashboard sau khi đăng nhập"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    return render_template('dashboard.html', 
                         full_name=session.get('full_name'), 
                         username=session.get('username'),
                         email=session.get('email'))

@main_bp.route('/profile')
def profile():
    """Trang thông tin cá nhân"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    return render_template('profile.html',
                         full_name=session.get('full_name'),
                         username=session.get('username'),
                         email=session.get('email'))

@main_bp.route('/update_profile', methods=['POST'])
def update_profile():
    """Cập nhật thông tin cá nhân"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login!'})
    
    full_name = request.form.get('full_name', '').strip()
    email = request.form.get('email', '').strip()
    
    # Validation
    if not email:
        return jsonify({'success': False, 'message': 'Please enter your email!'})
    
    if '@' not in email or '.' not in email:
        return jsonify({'success': False, 'message': 'Invalid email format!'})
    
    # Cập nhật thông tin
    if User.update_user(session['user_id'], full_name, email):
        session['full_name'] = full_name
        session['email'] = email
        return jsonify({'success': True, 'message': 'Profile updated successfully!'})
    else:
        return jsonify({'success': False, 'message': 'Email is already used by another user!'})

@main_bp.route('/change_password', methods=['POST'])
def change_password():
    """Đổi mật khẩu"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login!'})
    
    current_password = request.form.get('current_password', '').strip()
    new_password = request.form.get('new_password', '').strip()
    confirm_password = request.form.get('confirm_password', '').strip()
    
    # Validation
    if not current_password or not new_password or not confirm_password:
        return jsonify({'success': False, 'message': 'Please fill in all fields!'})
    
    if new_password != confirm_password:
        return jsonify({'success': False, 'message': 'Passwords do not match!'})
    
    if len(new_password) < 6:
        return jsonify({'success': False, 'message': 'New password must be at least 6 characters!'})
    
    # Kiểm tra mật khẩu hiện tại
    user = User.verify_user(session['username'], current_password)
    if not user:
        return jsonify({'success': False, 'message': 'Current password is incorrect!'})
    
    # Đổi mật khẩu
    if User.change_password(session['user_id'], new_password):
        return jsonify({'success': True, 'message': 'Password changed successfully!'})
    else:
        return jsonify({'success': False, 'message': 'Error changing password!'})



@main_bp.route('/cart')
def cart():
    """Trang giỏ hàng - hiển thị CartItem và tính tổng tiền"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    cart_id = Cart.get_or_create_cart(session['user_id'])
    if not cart_id:
        return render_template('cart.html', cart_items=[], subtotal=0.0, total=0.0)
    
    cart_items = CartItem.get_cart_items(cart_id)
    subtotal = Cart.get_cart_subtotal(cart_id)
    total = subtotal  # Có thể thêm shipping sau
    
    for item in cart_items:
        product = Product.get_product_by_id(item['product_id'])
        if product:
            item['product_name'] = product['name']
            item['product_color'] = product.get('color', 'N/A')
            item['price'] = float(product['price'])
            item['subtotal'] = item['price'] * item['quantity']
            item['image_url'] = product.get('image_url', '')
    
    return render_template('cart.html', 
                           cart_items=cart_items, 
                           subtotal=subtotal, 
                           total=total)

@main_bp.route('/update_cart', methods=['POST'])
def update_cart():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login!'})
    
    cart_id = Cart.get_or_create_cart(session['user_id'])
    if not cart_id:
        return jsonify({'success': False, 'message': 'Error getting cart!'})
    
    action = request.form.get('action')
    product_id = request.form.get('product_id')
    if not product_id:
        return jsonify({'success': False, 'message': 'Invalid product ID!'})
    product_id = int(product_id)
    
    if action == 'remove':
        if CartItem.remove_from_cart(cart_id, product_id):
            subtotal = Cart.get_cart_subtotal(cart_id)
            total = subtotal
            return jsonify({'success': True, 'item_id': product_id, 'subtotal': subtotal, 'total': total})
        else:
            return jsonify({'success': False, 'message': 'Error removing item!'})
    
    elif action == 'update':
        quantity = request.form.get('quantity')
        if not quantity:
            return jsonify({'success': False, 'message': 'Invalid quantity!'})
        quantity = int(quantity)
        if CartItem.update_quantity(cart_id, product_id, quantity):
            subtotal = Cart.get_cart_subtotal(cart_id)
            total = subtotal
            product = Product.get_product_by_id(product_id)
            item_subtotal = float(product['price']) * quantity if quantity > 0 and product else 0
            return jsonify({'success': True, 'item_id': product_id, 'item_subtotal': item_subtotal, 'subtotal': subtotal, 'total': total})
        else:
            return jsonify({'success': False, 'message': 'Error updating quantity!'})
    
    return jsonify({'success': False, 'message': 'Invalid action!'})