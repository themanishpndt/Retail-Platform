/**
 * Inventory API Integration
 * Handles all API calls for inventory management functionality
 */

// API Base URL
const INVENTORY_API = '/api/v1/inventory/';

class InventoryAPI {
    /**
     * Get inventory levels
     */
    static async getInventoryLevels(filters = {}) {
        try {
            const params = new URLSearchParams(filters);
            const response = await fetch(`${INVENTORY_API}levels/?${params}`, {
                headers: {
                    'Authorization': `Bearer ${getAuthToken()}`,
                    'Content-Type': 'application/json'
                }
            });
            return await response.json();
        } catch (error) {
            showAlert('Error fetching inventory levels', 'error');
            console.error('Error:', error);
            return null;
        }
    }

    /**
     * Get stores
     */
    static async getStores() {
        try {
            const response = await fetch(`${INVENTORY_API}stores/`, {
                headers: {
                    'Authorization': `Bearer ${getAuthToken()}`,
                    'Content-Type': 'application/json'
                }
            });
            return await response.json();
        } catch (error) {
            console.error('Error fetching stores:', error);
            return [];
        }
    }

    /**
     * Adjust stock
     */
    static async adjustStock(inventoryId, quantity, reason = 'adjustment') {
        try {
            const response = await fetch(`${INVENTORY_API}levels/${inventoryId}/`, {
                method: 'PATCH',
                headers: {
                    'Authorization': `Bearer ${getAuthToken()}`,
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    quantity: quantity,
                    adjustment_reason: reason
                })
            });
            const data = await response.json();
            showAlert('Stock adjusted successfully', 'success');
            return data;
        } catch (error) {
            showAlert('Error adjusting stock', 'error');
            console.error('Error:', error);
            return null;
        }
    }

    /**
     * Transfer stock between stores
     */
    static async transferStock(fromStoreId, toStoreId, productId, quantity) {
        try {
            const response = await fetch(`${INVENTORY_API}movements/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${getAuthToken()}`,
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    from_store_id: fromStoreId,
                    to_store_id: toStoreId,
                    product_id: productId,
                    quantity: quantity,
                    movement_type: 'transfer'
                })
            });
            const data = await response.json();
            showAlert('Stock transferred successfully', 'success');
            return data;
        } catch (error) {
            showAlert('Error transferring stock', 'error');
            console.error('Error:', error);
            return null;
        }
    }

    /**
     * Get inventory transactions
     */
    static async getTransactions(filters = {}) {
        try {
            const params = new URLSearchParams(filters);
            const response = await fetch(`${INVENTORY_API}transactions/?${params}`, {
                headers: {
                    'Authorization': `Bearer ${getAuthToken()}`,
                    'Content-Type': 'application/json'
                }
            });
            return await response.json();
        } catch (error) {
            console.error('Error fetching transactions:', error);
            return [];
        }
    }

    /**
     * Get low stock alert items
     */
    static async getLowStockItems() {
        try {
            const response = await fetch(`${INVENTORY_API}levels/?status=low`, {
                headers: {
                    'Authorization': `Bearer ${getAuthToken()}`,
                    'Content-Type': 'application/json'
                }
            });
            return await response.json();
        } catch (error) {
            console.error('Error fetching low stock items:', error);
            return [];
        }
    }
}

// Event listeners for buttons
document.addEventListener('DOMContentLoaded', function() {
    // Adjust Stock button
    const adjustBtn = document.querySelector('[data-action="adjust-stock"]');
    if (adjustBtn) {
        adjustBtn.addEventListener('click', openAdjustStockModal);
    }

    // Transfer Stock button
    const transferBtn = document.querySelector('[data-action="transfer-stock"]');
    if (transferBtn) {
        transferBtn.addEventListener('click', openTransferStockModal);
    }

    // Filter form
    const filterForm = document.querySelector('[data-form="inventory-filter"]');
    if (filterForm) {
        filterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            applyInventoryFilters();
        });
    }

    // View details buttons
    document.querySelectorAll('[data-action="view-details"]').forEach(btn => {
        btn.addEventListener('click', function() {
            const inventoryId = this.dataset.inventoryId;
            window.location.href = `/inventory/${inventoryId}/`;
        });
    });
});

// Open adjust stock modal
function openAdjustStockModal() {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'adjustStockModal';
    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Adjust Stock</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="adjustStockForm">
                        <div class="mb-3">
                            <label class="form-label">Product</label>
                            <select class="form-select" id="productSelect" required>
                                <option>Select a product...</option>
                            </select>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Store</label>
                            <select class="form-select" id="storeSelect" required>
                                <option>Select a store...</option>
                            </select>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Quantity Change</label>
                            <input type="number" class="form-control" id="quantityChange" placeholder="Enter positive or negative number" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Reason</label>
                            <select class="form-select" id="adjustmentReason">
                                <option value="physical_count">Physical Count</option>
                                <option value="damaged">Damaged</option>
                                <option value="loss">Loss/Theft</option>
                                <option value="correction">Correction</option>
                                <option value="other">Other</option>
                            </select>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    <button type="button" class="btn btn-primary" id="adjustStockBtn">Adjust Stock</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    const bootstrapModal = new bootstrap.Modal(modal);
    
    // Load data
    loadProducts('productSelect');
    loadStores('storeSelect');
    
    // Adjust stock handler
    document.getElementById('adjustStockBtn').addEventListener('click', function() {
        const productId = document.getElementById('productSelect').value;
        const storeId = document.getElementById('storeSelect').value;
        const quantity = document.getElementById('quantityChange').value;
        const reason = document.getElementById('adjustmentReason').value;
        
        // Find inventory record and adjust
        InventoryAPI.getInventoryLevels({product_id: productId, store_id: storeId}).then(result => {
            const data = Array.isArray(result) ? result[0] : result.results?.[0];
            if (data) {
                InventoryAPI.adjustStock(data.id, quantity, reason).then(() => {
                    bootstrapModal.hide();
                    location.reload();
                });
            }
        });
    });
    
    bootstrapModal.show();
    modal.addEventListener('hidden.bs.modal', () => modal.remove());
}

// Open transfer stock modal
function openTransferStockModal() {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'transferStockModal';
    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Transfer Stock</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="transferStockForm">
                        <div class="mb-3">
                            <label class="form-label">Product</label>
                            <select class="form-select" id="transferProductSelect" required>
                                <option>Select a product...</option>
                            </select>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">From Store</label>
                            <select class="form-select" id="fromStoreSelect" required>
                                <option>Select store...</option>
                            </select>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">To Store</label>
                            <select class="form-select" id="toStoreSelect" required>
                                <option>Select store...</option>
                            </select>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Quantity</label>
                            <input type="number" class="form-control" id="transferQuantity" placeholder="Enter quantity" min="1" required>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    <button type="button" class="btn btn-primary" id="transferStockBtn">Transfer Stock</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    const bootstrapModal = new bootstrap.Modal(modal);
    
    // Load data
    loadProducts('transferProductSelect');
    loadStores('fromStoreSelect');
    loadStores('toStoreSelect');
    
    // Transfer stock handler
    document.getElementById('transferStockBtn').addEventListener('click', function() {
        const fromStoreId = document.getElementById('fromStoreSelect').value;
        const toStoreId = document.getElementById('toStoreSelect').value;
        const productId = document.getElementById('transferProductSelect').value;
        const quantity = document.getElementById('transferQuantity').value;
        
        InventoryAPI.transferStock(fromStoreId, toStoreId, productId, quantity).then(() => {
            bootstrapModal.hide();
            location.reload();
        });
    });
    
    bootstrapModal.show();
    modal.addEventListener('hidden.bs.modal', () => modal.remove());
}

// Apply filters
function applyInventoryFilters() {
    const filters = {
        store: document.querySelector('[name="store"]')?.value || '',
        status: document.querySelector('[name="status"]')?.value || '',
        search: document.querySelector('[name="search"]')?.value || ''
    };
    
    // Build query string
    const queryString = Object.entries(filters)
        .filter(([_, v]) => v !== '')
        .map(([k, v]) => `${k}=${encodeURIComponent(v)}`)
        .join('&');
    
    window.location.search = queryString;
}

// Helper function to load products
async function loadProducts(selectId) {
    try {
        const response = await fetch('/api/v1/products/', {
            headers: {
                'Authorization': `Bearer ${getAuthToken()}`,
                'Content-Type': 'application/json'
            }
        });
        const data = await response.json();
        const select = document.getElementById(selectId);
        const products = Array.isArray(data) ? data : data.results || [];
        
        products.forEach(product => {
            const option = document.createElement('option');
            option.value = product.id;
            option.textContent = product.name;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading products:', error);
    }
}

// Helper function to load stores
async function loadStores(selectId) {
    try {
        const data = await InventoryAPI.getStores();
        const select = document.getElementById(selectId);
        const stores = Array.isArray(data) ? data : data.results || [];
        
        stores.forEach(store => {
            const option = document.createElement('option');
            option.value = store.id;
            option.textContent = store.name;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading stores:', error);
    }
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
