from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from website.models import User, CartItem, Cart, Product, Order

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Trang chủ - chuyển hướng đến đăng nhập"""
    return redirect(url_for('auth.login'))

@main_bp.route('/base')
def base():
    """Trang dashboard sau khi đăng nhập"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    return render_template('base.html', 
                         full_name=session.get('full_name'), 
                         username=session.get('username'),
                         email=session.get('email'))

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

@main_bp.route('/checkout')
def checkout():
    """Trang checkout - lấy thông tin từ shopping cart"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # Lấy thông tin giỏ hàng từ database
    cart_id = Cart.get_or_create_cart(session['user_id'])
    if not cart_id:
        return render_template('check-out.html', cart_items=[], subtotal=0.0, total=0.0)
    
    cart_items = CartItem.get_cart_items(cart_id)
    subtotal = Cart.get_cart_subtotal(cart_id)
    total = subtotal  # Có thể thêm shipping, tax sau
    
    # Thêm thông tin sản phẩm vào cart_items
    for item in cart_items:
        product = Product.get_product_by_id(item['product_id'])
        if product:
            item['product_name'] = product['name']
            item['product_color'] = product.get('color', 'N/A')
            item['price'] = float(product['price'])
            item['subtotal'] = item['price'] * item['quantity']
            item['image_url'] = product.get('image_url', '')
            item['product_id'] = product['id']  # Đảm bảo có product_id
    
    return render_template('check-out.html', 
                         cart_items=cart_items, 
                         subtotal=subtotal, 
                         total=total)

@main_bp.route('/place_order', methods=['POST'])
def place_order():
    """Xử lý đặt hàng từ checkout"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login!'})
    
    try:
        # Lấy thông tin từ form
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        street_address = request.form.get('street-address')
        country = request.form.get('country')
        city = request.form.get('city')
        state = request.form.get('state')
        zip_code = request.form.get('zip_code')
        
        # Validation
        if not all([first_name, last_name, email, street_address, country, city]):
            return jsonify({'success': False, 'message': 'Please fill in all required fields!'})
        
        # Lấy thông tin giỏ hàng
        cart_id = Cart.get_or_create_cart(session['user_id'])
        if not cart_id:
            return jsonify({'success': False, 'message': 'Cart not found!'})
        
        cart_items = CartItem.get_cart_items_with_products(cart_id)
        if not cart_items:
            return jsonify({'success': False, 'message': 'Cart is empty!'})
        
        # Tính tổng tiền
        total_amount = sum(item['subtotal'] for item in cart_items)
        
        # Chuẩn bị thông tin khách hàng
        customer_info = {
            'customer_name': f"{first_name} {last_name}",
            'customer_email': email,
            'customer_phone': phone,
            'shipping_address': f"{street_address}, {city}, {state}, {country}, {zip_code}".strip(', ')
        }
        
        # 🎯 Lưu order vào database
        order_id = Order.create_order(session['user_id'], cart_items, customer_info, total_amount)
        if not order_id:
            return jsonify({'success': False, 'message': 'Error creating order! Please try again.'})
        
        # 🎯 Xóa giỏ hàng sau khi đặt hàng thành công
        if not CartItem.clear_cart(cart_id):  # ← ĐÃ SỬA
            print("Warning: Could not clear cart, but order was created")
        
        return jsonify({
            'success': True, 
            'message': 'Order placed successfully!',
            'order_id': order_id,
            'order_details': customer_info,
            'redirect_url': url_for('main.order_complete', order_id=order_id)
        })
        
    except Exception as e:
        print(f"Error placing order: {e}")
        return jsonify({'success': False, 'message': 'Error placing order!'})

@main_bp.route('/order_complete')
def order_complete():
    """Trang xác nhận đơn hàng thành công"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    return render_template('complete.html')

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
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'})
    
    data = request.get_json()
    user_id = session['user_id']
    
    try:
        # Cập nhật trong database - sử dụng User.get_db_connection()
        conn = User.get_db_connection()
        if conn is None:
            return jsonify({'success': False, 'message': 'Database connection error'})
        
        cursor = conn.cursor()
        
        # CẬP NHẬT QUAN TRỌNG:
        full_name = f"{data['first_name']} {data['last_name']}"
        cursor.execute("""
            UPDATE users 
            SET full_name = %s, email = %s 
            WHERE id = %s
        """, (full_name, data['email'], user_id))
        conn.commit()
        
        # CẬP NHẬT SESSION
        session['full_name'] = data['first_name'] + ' ' + data['last_name']
        session['display_name'] = data['display_name']
        session['first_name'] = data['first_name']
        session['last_name'] = data['last_name']
        session['email'] = data['email']
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Profile updated successfully', 'session_updated': True})
        
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return jsonify({'success': False, 'message': str(e)})
