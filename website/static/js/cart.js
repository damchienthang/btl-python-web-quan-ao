document.addEventListener('DOMContentLoaded', function() {
     
        document.querySelectorAll('.remove-item').forEach(button => {
          button.addEventListener('click', function() {
            const itemElement = this.closest('.elements-cart');
            const productId = itemElement.dataset.itemId;
            updateCart('remove', productId, itemElement);
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
              updateCart('update', productId, itemElement, quantity);
            }
          });
        });

        document.querySelectorAll('.increase-quantity').forEach(button => {
          button.addEventListener('click', function() {
            const itemElement = this.closest('.elements-cart');
            const productId = itemElement.dataset.itemId;
            const quantityElement = itemElement.querySelector('.quantity');
            let quantity = parseInt(quantityElement.textContent);
            quantity++;
            updateCart('update', productId, itemElement, quantity);
          });
        });

        function updateCart(action, productId, itemElement, quantity = null) {
          const formData = new FormData();
          formData.append('action', action);
          formData.append('product_id', productId);
          if (quantity !== null) {
            formData.append('quantity', quantity);
          }

          fetch('/update_cart', {
            method: 'POST',
            body: formData
          })
          .then(response => response.json())
          .then(data => {
            if (data.success) {
              if (action === 'remove') {
                itemElement.remove();
              } else if (action === 'update') {
                const quantityElement = itemElement.querySelector('.quantity');
                const itemSubtotalElement = itemElement.querySelector('.item-subtotal');
                quantityElement.textContent = quantity;
                itemSubtotalElement.textContent = '$' + data.item_subtotal.toFixed(2);
              }

              document.querySelector('.subtotal').textContent = '$' + data.subtotal.toFixed(2);
              document.querySelector('.total').textContent = '$' + data.total.toFixed(2);
              document.querySelector('.text-wrapper-2').textContent = document.querySelectorAll('.elements-cart').length;
            } else {
              alert(data.message || 'Error updating cart!');
            }
          })
          .catch(error => console.error('Error:', error));
        }
      });

