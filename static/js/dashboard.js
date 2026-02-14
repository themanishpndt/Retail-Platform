// Dashboard JavaScript
// Handles data fetching and chart rendering

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    initializeSidebar();
    loadDashboardData();
    
    // Refresh data every 5 minutes
    setInterval(loadDashboardData, 300000);
});

// Sidebar toggle
function initializeSidebar() {
    const menuToggle = document.getElementById('menu-toggle');
    if (menuToggle) {
        menuToggle.addEventListener('click', function(e) {
            e.preventDefault();
            document.getElementById('wrapper').classList.toggle('toggled');
        });
    }
}

// Load all dashboard data
async function loadDashboardData() {
    try {
        // Load data from backend context or API
        await loadKPIsFromContext();
        await loadSampleCharts();
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        loadFallbackData();
    }
}

// Load KPIs from Django context or generate sample data
async function loadKPIsFromContext() {
    try {
        // Try to fetch real data from API
        const response = await fetch('/api/dashboard/');
        if (response.ok) {
            const data = await response.json();
            
            document.getElementById('total-revenue').textContent = `$${formatNumber(data.kpis.total_revenue)}`;
            document.getElementById('total-orders').textContent = formatNumber(data.kpis.total_orders);
            document.getElementById('low-stock-count').textContent = formatNumber(data.kpis.low_stock_count);
            document.getElementById('avg-order-value').textContent = `$${formatNumber(data.kpis.avg_order_value)}`;
            
            // Update charts with real data if available
            if (data.sales_trend && data.sales_trend.dates.length > 0) {
                loadRealSalesTrend(data.sales_trend);
            }
            if (data.top_products && data.top_products.labels.length > 0) {
                loadRealTopProducts(data.top_products);
            }
            if (data.inventory) {
                loadRealInventoryStatus(data.inventory);
            }
        } else {
            // Fallback to sample data
            loadSampleData();
        }
    } catch (error) {
        console.error('Error loading KPIs:', error);
        // Fallback to sample data
        loadSampleData();
    }
}

// Load sample data as fallback
function loadSampleData() {
    const randomRevenue = Math.floor(Math.random() * 50000) + 10000;
    const randomOrders = Math.floor(Math.random() * 200) + 50;
    const randomLowStock = Math.floor(Math.random() * 30) + 5;
    
    document.getElementById('total-revenue').textContent = `$${formatNumber(randomRevenue)}`;
    document.getElementById('total-orders').textContent = formatNumber(randomOrders);
    document.getElementById('low-stock-count').textContent = formatNumber(randomLowStock);
    document.getElementById('avg-order-value').textContent = `$${formatNumber(randomRevenue / randomOrders)}`;
}

// Load sample charts
function loadSampleCharts() {
    loadSalesTrend();
    loadTopProducts();
    loadInventoryStatus();
    loadForecast();
    loadAlerts();
    loadInsights();
}

// Load sales trend chart
function loadSalesTrend() {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Revenue',
                    data: revenues,
                    borderColor: '#4e73df',
                    backgroundColor: 'rgba(78, 115, 223, 0.1)',
                    tension: 0.3,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '$' + formatNumber(value);
                            }
                        }
                    }
                }
            }
        });
        
    } catch (error) {
        console.error('Error loading sales trend:', error);
    }
}

// Load sales trend chart
function loadSalesTrend() {
    const ctx = document.getElementById('salesTrendChart');
    if (!ctx) return;
    
    // Generate sample data for 30 days
    const labels = [];
    const revenues = [];
    for (let i = 29; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
        revenues.push(Math.floor(Math.random() * 5000) + 1000);
    }
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Revenue',
                data: revenues,
                borderColor: '#4e73df',
                backgroundColor: 'rgba(78, 115, 223, 0.05)',
                borderWidth: 2,
                tension: 0.3,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + formatNumber(value);
                        }
                    }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

// Load sales trend with real data
function loadRealSalesTrend(data) {
    const ctx = document.getElementById('salesTrendChart');
    if (!ctx) return;
    
    // Format dates
    const labels = data.dates.map(date => {
        const d = new Date(date);
        return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    });
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Revenue',
                data: data.revenues,
                borderColor: '#4e73df',
                backgroundColor: 'rgba(78, 115, 223, 0.05)',
                borderWidth: 2,
                tension: 0.3,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + formatNumber(value);
                        }
                    }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

// Load top products chart
function loadTopProducts() {
    const ctx = document.getElementById('topProductsChart');
    if (!ctx) return;
    
    // Sample data
    const products = ['Product A', 'Product B', 'Product C', 'Product D', 'Product E'];
    const revenues = products.map(() => Math.floor(Math.random() * 3000) + 500);
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: products,
            datasets: [{
                data: revenues,
                backgroundColor: [
                    '#4e73df',
                    '#1cc88a',
                    '#36b9cc',
                    '#f6c23e',
                    '#e74a3b'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Load top products with real data
function loadRealTopProducts(data) {
    const ctx = document.getElementById('topProductsChart');
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.labels,
            datasets: [{
                data: data.revenues,
                backgroundColor: [
                    '#4e73df',
                    '#1cc88a',
                    '#36b9cc',
                    '#f6c23e',
                    '#e74a3b'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Load inventory status chart
function loadInventoryStatus() {
    const ctx = document.getElementById('inventoryStatusChart');
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Low Stock', 'Overstock', 'Normal'],
            datasets: [{
                label: 'Items',
                data: [
                    Math.floor(Math.random() * 30) + 5,
                    Math.floor(Math.random() * 20) + 2,
                    Math.floor(Math.random() * 100) + 50
                ],
                backgroundColor: [
                    '#f6c23e',
                    '#e74a3b',
                    '#1cc88a'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

// Load inventory status with real data
function loadRealInventoryStatus(data) {
    const ctx = document.getElementById('inventoryStatusChart');
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Low Stock', 'Out of Stock', 'Overstock', 'Normal'],
            datasets: [{
                label: 'Items',
                data: [
                    data.low_stock || 0,
                    data.out_of_stock || 0,
                    data.overstock || 0,
                    data.normal || 0
                ],
                backgroundColor: [
                    '#f6c23e',
                    '#e74a3b',
                    '#858796',
                    '#1cc88a'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

// Load demand forecast chart
function loadForecast() {
    const ctx = document.getElementById('forecastChart');
    if (!ctx) return;
    
    // Generate sample forecast data for next 7 days
    const labels = [];
    const predictions = [];
    for (let i = 0; i < 7; i++) {
        const date = new Date();
        date.setDate(date.getDate() + i);
        labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
        predictions.push(Math.floor(Math.random() * 200) + 50);
    }
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Forecasted Demand',
                data: predictions,
                borderColor: '#36b9cc',
                backgroundColor: 'rgba(54, 185, 204, 0.1)',
                tension: 0.3,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Load active alerts
function loadAlerts() {
    const alertsList = document.getElementById('alerts-list');
    if (!alertsList) return;
    
    // Sample alerts
    const sampleAlerts = [
        { title: 'Low Stock Alert', message: '5 products below reorder point', severity: 'warning', time: new Date() },
        { title: 'Demand Spike', message: 'Product A showing 40% increase', severity: 'info', time: new Date() },
        { title: 'Out of Stock', message: '2 products completely out of stock', severity: 'danger', time: new Date() }
    ];
    
    if (sampleAlerts.length > 0) {
        alertsList.innerHTML = sampleAlerts.map(alert => `
            <div class="alert alert-${alert.severity} alert-dismissible fade show mb-2" role="alert">
                <strong>${alert.title}</strong> - ${alert.message}
                <small class="d-block text-muted">${alert.time.toLocaleString()}</small>
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `).join('');
    } else {
        alertsList.innerHTML = '<p class="text-muted">No active alerts</p>';
    }
}

// Load AI insights
function loadInsights() {
    const insightsList = document.getElementById('insights-list');
    if (!insightsList) return;
    
    // Sample insights
    const sampleInsights = [
        { title: 'Inventory Optimization', description: 'Consider reducing stock for low-turnover items', priority: 'High' },
        { title: 'Sales Trend', description: 'Weekend sales up 15% - adjust staffing', priority: 'Medium' },
        { title: 'Supplier Performance', description: 'Supplier B consistently late on deliveries', priority: 'Medium' }
    ];
    
    if (sampleInsights.length > 0) {
        insightsList.innerHTML = sampleInsights.map(insight => `
            <div class="card mb-2">
                <div class="card-body p-3">
                    <h6 class="card-title mb-1">${insight.title}
                        <span class="badge bg-primary float-end">${insight.priority}</span>
                    </h6>
                    <p class="card-text small mb-0">${insight.description}</p>
                </div>
            </div>
        `).join('');
    } else {
        insightsList.innerHTML = '<p class="text-muted">No insights available</p>';
    }
}

// Fallback data when API is unavailable
function loadFallbackData() {
    console.log('Loading fallback data');
    document.getElementById('total-revenue').textContent = '$0';
    document.getElementById('total-orders').textContent = '0';
    document.getElementById('low-stock-count').textContent = '0';
    document.getElementById('avg-order-value').textContent = '$0';
}

// Utility functions
function getAuthToken() {
    // In production, retrieve from localStorage or cookies
    return localStorage.getItem('auth_token') || '';
}

function formatNumber(num) {
    return new Intl.NumberFormat('en-US', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 2
    }).format(num);
}
