document.addEventListener('DOMContentLoaded', function() {
    // Xử lý form checkout - SỬA LẠI PHẦN NÀY
    const checkoutForm = document.getElementById('checkout-form');
    if (checkoutForm) {
        checkoutForm.addEventListener('submit', function(e) {
            e.preventDefault();
            placeOrder();
        });
    }

    // Xử lý nút Place Order riêng biệt
    const placeOrderBtn = document.querySelector('.show-more-wrapper');
    if (placeOrderBtn && !checkoutForm) {
        placeOrderBtn.addEventListener('click', function(e) {
            e.preventDefault();
            placeOrder();
        });
    }

    // Xử lý tăng/giảm số lượng trong checkout
    document.querySelectorAll('.increase-quantity').forEach(button => {
        button.addEventListener('click', function() {
            const itemElement = this.closest('.elements-cart');
            const productId = itemElement.dataset.itemId;
            const quantityElement = itemElement.querySelector('.quantity');
            let quantity = parseInt(quantityElement.textContent);
            quantity++;
            updateCartItem(productId, quantity, itemElement);
        });
    });

    document.querySelectorAll('.decrease-quantity').forEach(button => {
        button.addEventListener('click', function() {
            const itemElement = this.closest('.elements-cart');
            const productId = itemElement.dataset.itemId;
            const quantityElement = itemElement.querySelector('.quantity');
            let quantity = parseInt(quantityElement.textContent);
            if (quantity > 1) {
                quantity--;
                updateCartItem(productId, quantity, itemElement);
            }
        });
    });

    // Xử lý xóa sản phẩm
    document.querySelectorAll('.remove-item').forEach(button => {
        button.addEventListener('click', function() {
            const itemElement = this.closest('.elements-cart');
            const productId = this.dataset.itemId;
            removeCartItem(productId, itemElement);
        });
    });
    // Click vào step Shopping cart để quay lại trang cart
    const shoppingCartStep = document.querySelector('.frame-wrapper');
    if (shoppingCartStep) {
        shoppingCartStep.addEventListener('click', function() {
            window.location.href = '/cart';
        });
        shoppingCartStep.style.cursor = 'pointer';
    }
});

function placeOrder() {
    const formData = new FormData();
    
    // Lấy thông tin từ form
    formData.append('first_name', document.getElementById('input-1').value);
    formData.append('last_name', document.getElementById('input-2').value);
    formData.append('email', document.getElementById('input-4').value);
    formData.append('phone', document.getElementById('input-3').value);
    formData.append('street-address', document.querySelector('input[name="street-address"]').value);
    formData.append('country', document.querySelector('input[placeholder="Country"]').value);
    formData.append('city', document.querySelector('input[name="city"]').value);
    formData.append('state', document.querySelector('input[name="state"]').value);
    formData.append('zip_code', document.getElementById('input-5').value);

    fetch('/place_order', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Order placed successfully!');
            // Chuyển hướng đến trang confirmation
            window.location.href = '/order_complete';
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error placing order!');
    });
}

// THÊM CÁC HÀM CÒN THIẾU
function updateCartItem(productId, quantity, itemElement) {
    const formData = new FormData();
    formData.append('action', 'update');
    formData.append('product_id', productId);
    formData.append('quantity', quantity);

    fetch('/update_cart', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const quantityElement = itemElement.querySelector('.quantity');
            const itemSubtotalElement = itemElement.querySelector('.item-subtotal');
            quantityElement.textContent = quantity;
            itemSubtotalElement.textContent = '$' + data.item_subtotal.toFixed(2);
            
            // Cập nhật tổng tiền
            document.querySelector('.text-wrapper-17').textContent = '$' + data.subtotal.toFixed(2);
            document.querySelector('.free').textContent = '$' + data.total.toFixed(2);
        } else {
            alert(data.message || 'Error updating cart!');
        }
    })
    .catch(error => console.error('Error:', error));
}

function removeCartItem(productId, itemElement) {
    const formData = new FormData();
    formData.append('action', 'remove');
    formData.append('product_id', productId);

    fetch('/update_cart', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            itemElement.remove();
            // Cập nhật tổng tiền và số lượng
            document.querySelector('.text-wrapper-17').textContent = '$' + data.subtotal.toFixed(2);
            document.querySelector('.free').textContent = '$' + data.total.toFixed(2);
            document.querySelector('.text-wrapper-2').textContent = document.querySelectorAll('.elements-cart').length;
        } else {
            alert(data.message || 'Error removing item!');
        }
    })
    .catch(error => console.error('Error:', error));
}

// Thêm vào checkout.js
document.addEventListener('DOMContentLoaded', function() {
  // Click vào step Shopping cart để quay lại trang cart
  const shoppingCartStep = document.querySelector('.frame-wrapper');
  if (shoppingCartStep) {
    shoppingCartStep.addEventListener('click', function() {
      window.location.href = '/cart';
    });
    // Thêm cursor pointer để biểu thị có thể click
    shoppingCartStep.style.cursor = 'pointer';
  }
});
