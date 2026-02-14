/**
 * Orders API Integration
 * Handles all API calls for order management functionality
 */

// API Base URL
const ORDERS_API = '/api/v1/orders/';

class OrdersAPI {
    /**
     * Get orders list
     */
    static async getOrders(filters = {}) {
        try {
            const params = new URLSearchParams(filters);
            const response = await fetch(`${ORDERS_API}orders/?${params}`, {
                headers: {
                    'Authorization': `Bearer ${getAuthToken()}`,
                    'Content-Type': 'application/json'
                }
            });
            return await response.json();
        } catch (error) {
            showAlert('Error fetching orders', 'error');
            console.error('Error:', error);
            return null;
        }
    }

    /**
     * Get single order
     */
    static async getOrder(orderId) {
        try {
            const response = await fetch(`${ORDERS_API}orders/${orderId}/`, {
                headers: {
                    'Authorization': `Bearer ${getAuthToken()}`,
                    'Content-Type': 'application/json'
                }
            });
            return await response.json();
        } catch (error) {
            console.error('Error fetching order:', error);
            return null;
        }
    }

    /**
     * Create new order
     */
    static async createOrder(orderData) {
        try {
            const response = await fetch(`${ORDERS_API}orders/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${getAuthToken()}`,
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(orderData)
            });
            const data = await response.json();
            showAlert('Order created successfully', 'success');
            return data;
        } catch (error) {
            showAlert('Error creating order', 'error');
            console.error('Error:', error);
            return null;
        }
    }

    /**
     * Update order status
     */
    static async updateOrderStatus(orderId, status) {
        try {
            const response = await fetch(`${ORDERS_API}orders/${orderId}/`, {
                method: 'PATCH',
                headers: {
                    'Authorization': `Bearer ${getAuthToken()}`,
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    status: status
                })
            });
            const data = await response.json();
            showAlert(`Order status updated to ${status}`, 'success');
            return data;
        } catch (error) {
            showAlert('Error updating order status', 'error');
            console.error('Error:', error);
            return null;
        }
    }

    /**
     * Get customers
     */
    static async getCustomers() {
        try {
            const response = await fetch(`${ORDERS_API}customers/`, {
                headers: {
                    'Authorization': `Bearer ${getAuthToken()}`,
                    'Content-Type': 'application/json'
                }
            });
            return await response.json();
        } catch (error) {
            console.error('Error fetching customers:', error);
            return [];
        }
    }

    /**
     * Get order statistics
     */
    static async getOrderStats() {
        try {
            const response = await fetch(`${ORDERS_API}orders/?stats=true`, {
                headers: {
                    'Authorization': `Bearer ${getAuthToken()}`,
                    'Content-Type': 'application/json'
                }
            });
            return await response.json();
        } catch (error) {
            console.error('Error fetching order statistics:', error);
            return null;
        }
    }

    /**
     * Confirm order
     */
    static async confirmOrder(orderId) {
        try {
            const response = await fetch(`${ORDERS_API}orders/${orderId}/confirm/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${getAuthToken()}`,
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });
            const data = await response.json();
            showAlert('Order confirmed successfully', 'success');
            return data;
        } catch (error) {
            showAlert('Error confirming order', 'error');
            console.error('Error:', error);
            return null;
        }
    }

    /**
     * Cancel order
     */
    static async cancelOrder(orderId) {
        try {
            const response = await fetch(`${ORDERS_API}orders/${orderId}/`, {
                method: 'PATCH',
                headers: {
                    'Authorization': `Bearer ${getAuthToken()}`,
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    status: 'cancelled'
                })
            });
            const data = await response.json();
            showAlert('Order cancelled successfully', 'success');
            return data;
        } catch (error) {
            showAlert('Error cancelling order', 'error');
            console.error('Error:', error);
            return null;
        }
    }
}

// Event listeners for buttons
document.addEventListener('DOMContentLoaded', function() {
    // New Order button
    const newOrderBtn = document.querySelector('[data-action="new-order"]');
    if (newOrderBtn) {
        newOrderBtn.addEventListener('click', openCreateOrderModal);
    }

    // Filter form
    const filterForm = document.querySelector('[data-form="order-filter"]');
    if (filterForm) {
        filterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            applyOrderFilters();
        });
    }

    // View details buttons
    document.querySelectorAll('[data-action="view-order"]').forEach(btn => {
        btn.addEventListener('click', function() {
            const orderId = this.dataset.orderId;
            window.location.href = `/orders/${orderId}/`;
        });
    });

    // Confirm order buttons
    document.querySelectorAll('[data-action="confirm-order"]').forEach(btn => {
        btn.addEventListener('click', function() {
            const orderId = this.dataset.orderId;
            if (confirm('Are you sure you want to confirm this order?')) {
                OrdersAPI.confirmOrder(orderId).then(() => {
                    location.reload();
                });
            }
        });
    });

    // Cancel order buttons
    document.querySelectorAll('[data-action="cancel-order"]').forEach(btn => {
        btn.addEventListener('click', function() {
            const orderId = this.dataset.orderId;
            if (confirm('Are you sure you want to cancel this order?')) {
                OrdersAPI.cancelOrder(orderId).then(() => {
                    location.reload();
                });
            }
        });
    });
});

// Open create order modal
function openCreateOrderModal() {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'createOrderModal';
    modal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Create New Order</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="createOrderForm">
                        <div class="row mb-3">
                            <div class="col-md-6">
                                <label class="form-label">Customer</label>
                                <select class="form-select" id="customerSelect" required>
                                    <option>Select a customer...</option>
                                </select>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">Order Date</label>
                                <input type="date" class="form-control" id="orderDate" required>
                            </div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Products</label>
                            <div id="productsContainer">
                                <div class="row mb-2">
                                    <div class="col-md-6">
                                        <select class="form-select product-select" required>
                                            <option>Select product...</option>
                                        </select>
                                    </div>
                                    <div class="col-md-3">
                                        <input type="number" class="form-control product-qty" placeholder="Qty" min="1" required>
                                    </div>
                                    <div class="col-md-3">
                                        <input type="number" class="form-control product-price" placeholder="Price" step="0.01" required>
                                    </div>
                                </div>
                            </div>
                            <button type="button" class="btn btn-sm btn-secondary mt-2" id="addProductBtn">
                                <i class="fas fa-plus"></i> Add Product
                            </button>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Notes</label>
                            <textarea class="form-control" id="orderNotes" rows="3"></textarea>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    <button type="button" class="btn btn-primary" id="createOrderBtn">Create Order</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    const bootstrapModal = new bootstrap.Modal(modal);
    
    // Load data
    loadCustomers('customerSelect');
    loadProductsForOrder();
    
    // Set today's date
    document.getElementById('orderDate').valueAsDate = new Date();
    
    // Add product button
    document.getElementById('addProductBtn').addEventListener('click', function() {
        const container = document.getElementById('productsContainer');
        const newRow = document.createElement('div');
        newRow.className = 'row mb-2';
        newRow.innerHTML = `
            <div class="col-md-6">
                <select class="form-select product-select" required>
                    <option>Select product...</option>
                </select>
            </div>
            <div class="col-md-3">
                <input type="number" class="form-control product-qty" placeholder="Qty" min="1" required>
            </div>
            <div class="col-md-3">
                <input type="number" class="form-control product-price" placeholder="Price" step="0.01" required>
            </div>
        `;
        container.appendChild(newRow);
        loadProductsForOrder();
    });
    
    // Create order handler
    document.getElementById('createOrderBtn').addEventListener('click', function() {
        const customerId = document.getElementById('customerSelect').value;
        const orderDate = document.getElementById('orderDate').value;
        const note = document.getElementById('orderNotes').value;
        
        const lineItems = [];
        document.querySelectorAll('#productsContainer .row').forEach(row => {
            const productSelect = row.querySelector('.product-select');
            const qty = row.querySelector('.product-qty').value;
            const price = row.querySelector('.product-price').value;
            
            if (productSelect.value) {
                lineItems.push({
                    product_id: productSelect.value,
                    quantity: parseInt(qty),
                    unit_price: parseFloat(price)
                });
            }
        });
        
        if (lineItems.length === 0) {
            showAlert('Please add at least one product', 'warning');
            return;
        }
        
        const orderData = {
            customer_id: customerId,
            order_date: orderDate,
            line_items: lineItems,
            notes: note,
            status: 'pending'
        };
        
        OrdersAPI.createOrder(orderData).then((data) => {
            bootstrapModal.hide();
            location.reload();
        });
    });
    
    bootstrapModal.show();
    modal.addEventListener('hidden.bs.modal', () => modal.remove());
}

// Load products for order
async function loadProductsForOrder() {
    try {
        const response = await fetch('/api/v1/products/', {
            headers: {
                'Authorization': `Bearer ${getAuthToken()}`,
                'Content-Type': 'application/json'
            }
        });
        const data = await response.json();
        const products = Array.isArray(data) ? data : data.results || [];
        
        document.querySelectorAll('.product-select').forEach(select => {
            select.innerHTML = '<option>Select product...</option>';
            products.forEach(product => {
                const option = document.createElement('option');
                option.value = product.id;
                option.textContent = `${product.name} - $${product.price}`;
                option.dataset.price = product.price;
                select.appendChild(option);
            });
            
            // Auto-fill price on selection
            select.addEventListener('change', function() {
                if (this.value) {
                    const selectedOption = this.querySelector(`option[value="${this.value}"]`);
                    const priceInput = this.closest('.row').querySelector('.product-price');
                    if (selectedOption && selectedOption.dataset.price) {
                        priceInput.value = selectedOption.dataset.price;
                    }
                }
            });
        });
    } catch (error) {
        console.error('Error loading products:', error);
    }
}

// Load customers
async function loadCustomers(selectId) {
    try {
        const data = await OrdersAPI.getCustomers();
        const select = document.getElementById(selectId);
        const customers = Array.isArray(data) ? data : data.results || [];
        
        customers.forEach(customer => {
            const option = document.createElement('option');
            option.value = customer.id;
            option.textContent = customer.name;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading customers:', error);
    }
}

// Apply filters
function applyOrderFilters() {
    const filters = {
        status: document.querySelector('[name="status"]')?.value || '',
        from_date: document.querySelector('[name="from_date"]')?.value || '',
        to_date: document.querySelector('[name="to_date"]')?.value || ''
    };
    
    // Build query string
    const queryString = Object.entries(filters)
        .filter(([_, v]) => v !== '')
        .map(([k, v]) => `${k}=${encodeURIComponent(v)}`)
        .join('&');
    
    window.location.search = queryString;
}

// Helper function to show alerts
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.setAttribute('role', 'alert');
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    const container = document.querySelector('.container-fluid') || document.body;
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
    } else {
        document.body.insertBefore(alertDiv, document.body.firstChild);
    }
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Get auth token from localStorage
function getAuthToken() {
    return localStorage.getItem('auth_token') || '';
}
