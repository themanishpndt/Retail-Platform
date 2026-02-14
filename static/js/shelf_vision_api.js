/**
 * Shelf Vision API Integration
 * Handles all API calls for shelf vision/computer vision functionality
 */

// API Base URL
const SHELF_VISION_API = '/api/v1/vision/';

class ShelfVisionAPI {
    /**
     * Get shelf analysis data
     */
    static async getShelfAnalysis(filters = {}) {
        try {
            const params = new URLSearchParams(filters);
            const response = await fetch(`${SHELF_VISION_API}shelf-analysis/?${params}`, {
                headers: {
                    'Authorization': `Bearer ${getAuthToken()}`,
                    'Content-Type': 'application/json'
                }
            });
            return await response.json();
        } catch (error) {
            showAlert('Error fetching shelf analysis data', 'error');
            console.error('Error:', error);
            return null;
        }
    }

    /**
     * Get detection models
     */
    static async getDetectionModels() {
        try {
            const response = await fetch(`${SHELF_VISION_API}detection-models/`, {
                headers: {
                    'Authorization': `Bearer ${getAuthToken()}`,
                    'Content-Type': 'application/json'
                }
            });
            return await response.json();
        } catch (error) {
            console.error('Error fetching detection models:', error);
            return [];
        }
    }

    /**
     * Start live scan
     */
    static async startLiveScan() {
        try {
            const response = await fetch(`${SHELF_VISION_API}detection-tasks/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${getAuthToken()}`,
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    task_type: 'live_scan',
                    status: 'pending'
                })
            });
            const data = await response.json();
            showAlert('Live scan started', 'success');
            return data;
        } catch (error) {
            showAlert('Error starting live scan', 'error');
            console.error('Error:', error);
            return null;
        }
    }

    /**
     * Refresh data
     */
    static async refreshData() {
        try {
            const response = await fetch(`${SHELF_VISION_API}shelf-analysis/`, {
                headers: {
                    'Authorization': `Bearer ${getAuthToken()}`,
                    'Content-Type': 'application/json'
                }
            });
            const data = await response.json();
            showAlert('Data refreshed successfully', 'success');
            location.reload();
            return data;
        } catch (error) {
            showAlert('Error refreshing data', 'error');
            console.error('Error:', error);
            return null;
        }
    }

    /**
     * Rescan specific shelf
     */
    static async rescanShelf(shelfId) {
        try {
            const response = await fetch(`${SHELF_VISION_API}detection-tasks/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${getAuthToken()}`,
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    shelf_id: shelfId,
                    task_type: 'rescan',
                    status: 'pending'
                })
            });
            const data = await response.json();
            showAlert('Rescan initiated for shelf ' + shelfId, 'success');
            return data;
        } catch (error) {
            showAlert('Error initiating rescan', 'error');
            console.error('Error:', error);
            return null;
        }
    }

    /**
     * Get shelf image
     */
    static async getShelfImage(shelfId) {
        try {
            const response = await fetch(`${SHELF_VISION_API}shelf-analysis/${shelfId}/`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching shelf image:', error);
            return null;
        }
    }

    /**
     * Report issue for shelf
     */
    static async reportIssue(shelfId, issueDescription) {
        try {
            const response = await fetch(`${SHELF_VISION_API}shelf-analysis/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${getAuthToken()}`,
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    shelf_id: shelfId,
                    issue_description: issueDescription,
                    status: 'reported'
                })
            });
            const data = await response.json();
            showAlert('Issue reported successfully', 'success');
            return data;
        } catch (error) {
            showAlert('Error reporting issue', 'error');
            console.error('Error:', error);
            return null;
        }
    }
}

// Event listeners for buttons
document.addEventListener('DOMContentLoaded', function() {
    // Live Scan button
    const liveScanBtn = document.querySelector('[data-action="live-scan"]');
    if (liveScanBtn) {
        liveScanBtn.addEventListener('click', function() {
            ShelfVisionAPI.startLiveScan();
        });
    }

    // Refresh Data button
    const refreshBtn = document.querySelector('[data-action="refresh-data"]');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            ShelfVisionAPI.refreshData();
        });
    }

    // Rescan buttons for each shelf
    document.querySelectorAll('[data-action="rescan"]').forEach(btn => {
        btn.addEventListener('click', function() {
            const shelfId = this.dataset.shelfId;
            ShelfVisionAPI.rescanShelf(shelfId);
        });
    });

    // View image buttons
    document.querySelectorAll('[data-action="view-image"]').forEach(btn => {
        btn.addEventListener('click', function() {
            const shelfId = this.dataset.shelfId;
            ShelfVisionAPI.getShelfImage(shelfId).then(data => {
                if (data && data.image) {
                    showImageModal(data.image);
                }
            });
        });
    });

    // Report issue buttons
    document.querySelectorAll('[data-action="report-issue"]').forEach(btn => {
        btn.addEventListener('click', function() {
            const shelfId = this.dataset.shelfId;
            const description = prompt('Please describe the issue:');
            if (description) {
                ShelfVisionAPI.reportIssue(shelfId, description);
            }
        });
    });
});

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

// Helper function to show image modal
function showImageModal(imageSrc) {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'imageModal';
    modal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Shelf Image</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <img src="${imageSrc}" class="img-fluid" alt="Shelf Image">
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    new bootstrap.Modal(modal).show();
    modal.addEventListener('hidden.bs.modal', () => modal.remove());
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
