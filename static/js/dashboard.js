// Dashboard JavaScript - Updated to use Django context data
// Handles chart rendering with real data from backend

document.addEventListener('DOMContentLoaded', function() {
    initializeSidebar();
    initializeDashboardCharts();
});

// Sidebar toggle functionality
function initializeSidebar() {
    const menuToggle = document.getElementById('menu-toggle');
    if (menuToggle) {
        menuToggle.addEventListener('click', function(e) {
            e.preventDefault();
            const wrapper = document.getElementById('wrapper');
            if (wrapper) {
                wrapper.classList.toggle('toggled');
            }
        });
    }
}

// Initialize all dashboard charts with data from Django context
function initializeDashboardCharts() {
    if (typeof dashboardData === 'undefined') {
        console.warn('Dashboard data not found, loading sample data');
        loadSampleCharts();
        return;
    }
    
    loadSalesTrendChart(dashboardData.salesTrend);
    loadTopProductsChart(dashboardData.topProducts);
    loadInventoryStatusChart(dashboardData.inventoryByStore);
    loadForecastChart(dashboardData.forecastData);
}

// Sales Trend Chart
function loadSalesTrendChart(salesData) {
    const ctx = document.getElementById('salesTrendChart');
    if (!ctx) return;
    
    if (!salesData || salesData.length === 0) {
        loadSampleSalesTrend();
        return;
    }
    
    const labels = salesData.map(item => {
        const date = new Date(item.date);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    });
    
    const revenues = salesData.map(item => item.revenue);
    
    try {
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
                    fill: true,
                    pointRadius: 3,
                    pointBackgroundColor: '#4e73df'
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
                                return '$' + formatNumber(Math.round(value));
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading sales trend chart:', error);
    }
}

// Top Products Chart
function loadTopProductsChart(productsData) {
    const ctx = document.getElementById('topProductsChart');
    if (!ctx) return;
    
    if (!productsData || productsData.length === 0) {
        loadSampleTopProducts();
        return;
    }
    
    const labels = productsData.map(item => item.product__name);
    const quantities = productsData.map(item => item.total_sold);
    
    try {
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: quantities,
                    backgroundColor: [
                        '#4e73df',
                        '#858796',
                        '#1cc88a',
                        '#36b9cc',
                        '#f6c23e'
                    ],
                    borderColor: '#fff'
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
    } catch (error) {
        console.error('Error loading top products chart:', error);
    }
}

// Inventory Status Chart
function loadInventoryStatusChart(inventoryData) {
    const ctx = document.getElementById('inventoryStatusChart');
    if (!ctx) return;
    
    if (!inventoryData || inventoryData.length === 0) {
        loadSampleInventoryStatus();
        return;
    }
    
    const labels = inventoryData.map(item => item.store__name);
    const quantities = inventoryData.map(item => item.total_quantity || 0);
    
    try {
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Quantity on Hand',
                    data: quantities,
                    backgroundColor: '#1cc88a',
                    borderColor: '#1cc88a',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {
                    legend: {
                        display: true
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return formatNumber(value);
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading inventory chart:', error);
    }
}

// Forecast Chart
function loadForecastChart(forecastData) {
    const ctx = document.getElementById('forecastChart');
    if (!ctx) return;
    
    if (!forecastData || forecastData.length === 0) {
        loadSampleForecast();
        return;
    }
    
    const labels = forecastData.map(item => {
        const date = new Date(item.date);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    });
    
    const demand = forecastData.map(item => item.forecasted_demand);
    
    try {
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Forecasted Demand',
                    data: demand,
                    borderColor: '#f6c23e',
                    backgroundColor: 'rgba(246, 194, 62, 0.1)',
                    borderWidth: 2,
                    tension: 0.3,
                    fill: true,
                    pointRadius: 3,
                    pointBackgroundColor: '#f6c23e'
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
                                return formatNumber(Math.round(value));
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading forecast chart:', error);
    }
}

// Sample chart generators for fallback
function loadSampleSalesTrend() {
    const ctx = document.getElementById('salesTrendChart');
    if (!ctx) return;
    
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

function loadSampleTopProducts() {
    const ctx = document.getElementById('topProductsChart');
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Product A', 'Product B', 'Product C', 'Product D', 'Product E'],
            datasets: [{
                data: [30, 25, 20, 15, 10],
                backgroundColor: ['#4e73df', '#858796', '#1cc88a', '#36b9cc', '#f6c23e']
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

function loadSampleInventoryStatus() {
    const ctx = document.getElementById('inventoryStatusChart');
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Store A', 'Store B', 'Store C', 'Store D'],
            datasets: [{
                label: 'Quantity on Hand',
                data: [150, 200, 120, 180],
                backgroundColor: '#1cc88a'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: {
                legend: { display: true }
            }
        }
    });
}

function loadSampleForecast() {
    const ctx = document.getElementById('forecastChart');
    if (!ctx) return;
    
    const labels = [];
    const demand = [];
    for (let i = 0; i < 7; i++) {
        const date = new Date();
        date.setDate(date.getDate() + i);
        labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
        demand.push(Math.floor(Math.random() * 100) + 80);
    }
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Forecasted Demand',
                data: demand,
                borderColor: '#f6c23e',
                backgroundColor: 'rgba(246, 194, 62, 0.1)',
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
                    beginAtZero: true
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

function loadSampleCharts() {
    loadSampleSalesTrend();
    loadSampleTopProducts();
    loadSampleInventoryStatus();
    loadSampleForecast();
}

// Utility function to format numbers
function formatNumber(num) {
    if (num === null || num === undefined) return '0';
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}
