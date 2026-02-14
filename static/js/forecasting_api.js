/**
 * Forecasting API Integration
 * Handles all API calls for demand forecasting functionality
 */

// API Base URL
const FORECASTING_API = '/api/v1/forecasting/';

class ForecastingAPI {
    /**
     * Get forecast results
     */
    static async getForecastResults(filters = {}) {
        try {
            const params = new URLSearchParams(filters);
            const response = await fetch(`${FORECASTING_API}results/?${params}`, {
                headers: {
                    'Authorization': `Bearer ${getAuthToken()}`,
                    'Content-Type': 'application/json'
                }
            });
            return await response.json();
        } catch (error) {
            showAlert('Error fetching forecast results', 'error');
            console.error('Error:', error);
            return null;
        }
    }

    /**
     * Get forecast models
     */
    static async getForecastModels() {
        try {
            const response = await fetch(`${FORECASTING_API}models/`, {
                headers: {
                    'Authorization': `Bearer ${getAuthToken()}`,
                    'Content-Type': 'application/json'
                }
            });
            return await response.json();
        } catch (error) {
            console.error('Error fetching forecast models:', error);
            return [];
        }
    }

    /**
     * Create new forecast
     */
    static async createForecast(productId, forecastDays = 30) {
        try {
            const response = await fetch(`${FORECASTING_API}results/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${getAuthToken()}`,
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    product_id: productId,
                    forecast_days: forecastDays,
                    status: 'pending'
                })
            });
            const data = await response.json();
            showAlert('Forecast created successfully', 'success');
            return data;
        } catch (error) {
            showAlert('Error creating forecast', 'error');
            console.error('Error:', error);
            return null;
        }
    }

    /**
     * Get recommendations
     */
    static async getRecommendations(filters = {}) {
        try {
            const params = new URLSearchParams(filters);
            const response = await fetch(`${FORECASTING_API}recommendations/?${params}`, {
                headers: {
                    'Authorization': `Bearer ${getAuthToken()}`,
                    'Content-Type': 'application/json'
                }
            });
            return await response.json();
        } catch (error) {
            console.error('Error fetching recommendations:', error);
            return [];
        }
    }

    /**
     * Run forecast model
     */
    static async runForecastModel(modelId, productId) {
        try {
            const response = await fetch(`${FORECASTING_API}models/${modelId}/run/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${getAuthToken()}`,
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    product_id: productId
                })
            });
            const data = await response.json();
            showAlert('Model executed successfully', 'success');
            return data;
        } catch (error) {
            showAlert('Error executing model', 'error');
            console.error('Error:', error);
            return null;
        }
    }

    /**
     * Get forecast chart data
     */
    static async getForecastChartData(productId = null) {
        try {
            let url = `${FORECASTING_API}results/`;
            if (productId) {
                url += `?product_id=${productId}`;
            }
            const response = await fetch(url, {
                headers: {
                    'Authorization': `Bearer ${getAuthToken()}`,
                    'Content-Type': 'application/json'
                }
            });
            const data = await response.json();
            
            // Format data for chart
            const results = Array.isArray(data) ? data : data.results || [];
            return formatForecastChartData(results);
        } catch (error) {
            console.error('Error fetching chart data:', error);
            return null;
        }
    }
}

// Format data for chart.js
function formatForecastChartData(forecasts) {
    const labels = [];
    const forecastData = [];
    const confidenceData = [];

    forecasts.forEach(forecast => {
        labels.push(new Date(forecast.date).toLocaleDateString());
        forecastData.push(forecast.forecast);
        confidenceData.push(forecast.confidence || 85);
    });

    return {
        labels: labels,
        datasets: [
            {
                label: 'Forecast',
                data: forecastData,
                borderColor: '#0d6efd',
                backgroundColor: 'rgba(13, 110, 253, 0.1)',
                tension: 0.4
            },
            {
                label: 'Confidence (%)',
                data: confidenceData,
                borderColor: '#198754',
                backgroundColor: 'rgba(25, 135, 84, 0.1)',
                tension: 0.4,
                yAxisID: 'y1'
            }
        ]
    };
}

// Event listeners for buttons
document.addEventListener('DOMContentLoaded', function() {
    // New Forecast button
    const newForecastBtn = document.querySelector('[data-bs-target="#forecastModal"]');
    if (newForecastBtn) {
        newForecastBtn.addEventListener('click', function() {
            openForecastModal();
        });
    }

    // Render forecast chart if element exists
    const forecastChartCanvas = document.getElementById('forecastChart');
    if (forecastChartCanvas) {
        loadForecastChart();
    }

    // Run Model buttons
    document.querySelectorAll('[data-action="run-model"]').forEach(btn => {
        btn.addEventListener('click', function() {
            const modelId = this.dataset.modelId;
            const productId = this.dataset.productId;
            ForecastingAPI.runForecastModel(modelId, productId);
        });
    });
});

// Load and render forecast chart
async function loadForecastChart() {
    const data = await ForecastingAPI.getForecastChartData();
    if (!data) return;

    const ctx = document.getElementById('forecastChart').getContext('2d');
    const chart = new Chart(ctx, {
        type: 'line',
        data: data,
        options: {
            responsive: true,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    display: true,
                }
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Forecast Units'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Confidence %'
                    },
                    grid: {
                        drawOnChartArea: false,
                    }
                }
            }
        }
    });
}

// Open forecast creation modal
function openForecastModal() {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'forecastModal';
    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Create New Forecast</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="forecastForm">
                        <div class="mb-3">
                            <label class="form-label">Product</label>
                            <select class="form-select" id="productSelect" required>
                                <option>Select a product...</option>
                            </select>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Forecast Days</label>
                            <input type="number" class="form-control" id="forecastDays" value="30" min="7" max="365">
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    <button type="button" class="btn btn-primary" id="createForecastBtn">Create Forecast</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    const bootstrapModal = new bootstrap.Modal(modal);
    
    // Load products
    loadProducts('productSelect');
    
    // Create forecast handler
    document.getElementById('createForecastBtn').addEventListener('click', function() {
        const productId = document.getElementById('productSelect').value;
        const days = document.getElementById('forecastDays').value;
        ForecastingAPI.createForecast(productId, days).then(() => {
            bootstrapModal.hide();
            location.reload();
        });
    });
    
    bootstrapModal.show();
    modal.addEventListener('hidden.bs.modal', () => modal.remove());
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
    container.insertBefore(alertDiv, container.firstChild);
    
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
