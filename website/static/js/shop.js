 // Xử lý AJAX để thêm vào giỏ hàng mà không reload trang
        $(document).ready(function() {
            $('.add-to-cart-btn').on('click', function(e) {
                e.preventDefault();
                var productId = $(this).closest('.button-hover').data('product-id');
                $.ajax({
                    url: '/add_to_cart',
                    type: 'POST',
                    data: { product_id: productId },
                    success: function(response) {
                        if (response.success) {
                            showToast(response.message, 'success');
                            // Cập nhật số lượng giỏ hàng
                            if (response.cart_count !== undefined) {
                                $('.text-wrapper-2').text(response.cart_count);
                            }
                        } else {
                            showToast(response.message, 'error');
                        }
                    },
                    error: function() {
                        showToast('Lỗi kết nối!', 'error');
                    }
                });
            });

            // Xử lý lọc giá bằng AJAX
            $('input[name="price_range"]').on('change', function() {
                var priceRange = $(this).val();
                var categoryId = new URLSearchParams(window.location.search).get('category') || ''; // Lấy category nếu có

                $.ajax({
                    url: '/shop',
                    type: 'GET',
                    data: {
                        category: categoryId,
                        price_range: priceRange
                    },
                    // Trong success của AJAX lọc giá
                    success: function(response) {
                        $('#product-list').html($(response).find('#product-list').html());
                        
                        // Re-bind add-to-cart (vì elements mới)
                        $('.add-to-cart-btn').off('click').on('click', function(e) {
                            e.preventDefault();
                            var productId = $(this).closest('.button-hover').data('product-id');
                            $.ajax({
                                url: '/add_to_cart',
                                type: 'POST',
                                data: { product_id: productId },
                                success: function(response) {
                                    if (response.success) {
                                        showToast(response.message, 'success');
                                        // Cập nhật cart count nếu backend trả về
                                        if (response.cart_count !== undefined) {
                                            $('.text-wrapper-2').text(response.cart_count);
                                        }
                                    } else {
                                        showToast(response.message, 'error');
                                    }
                                },
                                error: function() {
                                    showToast('Lỗi kết nối!', 'error');
                                }
                            });
                        });
                    }
                });
            });

            function showToast(message, type = 'success') {
                $('#toast').text(message).removeClass('error').addClass(type === 'error' ? 'error' : '').fadeIn(500).delay(3000).fadeOut(500);
            }

            document.querySelector('.outlineshopping-bag-icon').addEventListener('click', () => {
                window.location.href = '/cart';
            });
            document.querySelector('.div').addEventListener('click', () => {
                window.location.href = '/shop';
            });
        });