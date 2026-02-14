/* ========================================================
   MODERN ADMIN DASHBOARD - JAVASCRIPT
   ======================================================== */

(function() {
    'use strict';

    // Initialize on page load
    document.addEventListener('DOMContentLoaded', function() {
        initSidebar();
        initSearch();
        initFilters();
        initTooltips();
        initAnimations();
        initDarkMode();
    });

    /**
     * Sidebar Navigation
     */
    function initSidebar() {
        const sidebar = document.querySelector('.sidebar');
        if (!sidebar) return;

        // Add active state to current page link
        const currentPath = window.location.pathname;
        const links = sidebar.querySelectorAll('a');
        
        links.forEach(link => {
            if (link.getAttribute('href') === currentPath) {
                link.closest('li').classList.add('active');
                link.style.backgroundColor = '#f0f0f0';
                link.style.borderLeftColor = 'var(--secondary)';
            }
        });

        // Toggle mobile sidebar
        const menuToggle = document.querySelector('.menu-toggle');
        if (menuToggle) {
            menuToggle.addEventListener('click', function() {
                sidebar.classList.toggle('show');
            });
        }

        // Close sidebar on link click (mobile)
        links.forEach(link => {
            link.addEventListener('click', function() {
                if (window.innerWidth < 1024) {
                    sidebar.classList.remove('show');
                }
            });
        });

        // Auto-collapse sidebar on small screens
        function handleResize() {
            if (window.innerWidth < 1024) {
                sidebar.classList.add('collapsed');
            } else {
                sidebar.classList.remove('collapsed');
            }
        }

        window.addEventListener('resize', handleResize);
        handleResize();
    }

    /**
     * Search Functionality
     */
    function initSearch() {
        const searchInput = document.querySelector('#searchbar input, input[type="search"]');
        if (!searchInput) return;

        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            
            if (query.length > 0) {
                searchTimeout = setTimeout(() => {
                    highlightSearchTerms(query);
                }, 300);
            }
        });

        // Add search icon animation
        const searchForm = searchInput.closest('form');
        if (searchForm) {
            searchForm.style.position = 'relative';
            const icon = document.createElement('i');
            icon.className = 'fas fa-search';
            icon.style.cssText = `
                position: absolute;
                right: 12px;
                top: 50%;
                transform: translateY(-50%);
                color: #999;
                pointer-events: none;
            `;
            searchForm.appendChild(icon);
        }
    }

    /**
     * Highlight Search Terms in Results
     */
    function highlightSearchTerms(term) {
        const table = document.querySelector('#result_list');
        if (!table) return;

        const rows = table.querySelectorAll('tbody tr');
        const regex = new RegExp(`(${term})`, 'gi');

        rows.forEach(row => {
            const cells = row.querySelectorAll('td');
            cells.forEach(cell => {
                if (cell.textContent.toLowerCase().includes(term.toLowerCase())) {
                    cell.innerHTML = cell.innerHTML.replace(
                        regex,
                        '<mark style="background-color: #fff59d; padding: 2px 4px; border-radius: 3px;">$1</mark>'
                    );
                }
            });
        });
    }

    /**
     * Filter Functionality
     */
    function initFilters() {
        const filters = document.querySelectorAll('#changelist-filter li');
        
        filters.forEach(filter => {
            const link = filter.querySelector('a');
            if (!link) return;

            link.addEventListener('click', function(e) {
                // Add animation
                this.style.transition = 'all 0.3s ease';
                this.style.transform = 'scale(0.95)';
                
                setTimeout(() => {
                    this.style.transform = 'scale(1)';
                }, 100);
            });
        });

        // Add filter counter
        const filterSection = document.querySelector('#changelist-filter');
        if (filterSection) {
            const selectedFilters = filterSection.querySelectorAll('.selected');
            if (selectedFilters.length > 0) {
                const badge = document.createElement('span');
                badge.className = 'badge bg-info';
                badge.textContent = selectedFilters.length;
                badge.style.marginLeft = '0.5rem';
                const filterHeader = filterSection.querySelector('h2');
                if (filterHeader) {
                    filterHeader.appendChild(badge);
                }
            }
        }
    }

    /**
     * Tooltips
     */
    function initTooltips() {
        // Bootstrap tooltips if available
        if (typeof bootstrap !== 'undefined') {
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(function(tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        }

        // Add custom tooltips for help text
        const helpTexts = document.querySelectorAll('.help-text');
        helpTexts.forEach(text => {
            text.style.cursor = 'help';
            text.addEventListener('mouseenter', function() {
                const tooltip = document.createElement('div');
                tooltip.className = 'custom-tooltip';
                tooltip.textContent = this.textContent;
                tooltip.style.cssText = `
                    position: absolute;
                    background: #333;
                    color: white;
                    padding: 8px 12px;
                    border-radius: 6px;
                    font-size: 12px;
                    z-index: 1000;
                    white-space: nowrap;
                    bottom: 120%;
                    left: 50%;
                    transform: translateX(-50%);
                    animation: tooltipFade 0.3s ease;
                `;
                this.style.position = 'relative';
                this.appendChild(tooltip);

                setTimeout(() => {
                    tooltip.remove();
                }, 3000);
            });
        });
    }

    /**
     * Animations
     */
    function initAnimations() {
        // Add animation classes to elements
        const cards = document.querySelectorAll('.stat-card, .dashboard-card, .module-card');
        
        cards.forEach((card, index) => {
            card.style.animation = `slideIn 0.3s ease ${index * 0.05}s both`;
        });

        // Intersection Observer for lazy animations
        if ('IntersectionObserver' in window) {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0)';
                        observer.unobserve(entry.target);
                    }
                });
            });

            document.querySelectorAll('.stat-card, .dashboard-card').forEach(el => {
                el.style.opacity = '0';
                el.style.transform = 'translateY(20px)';
                el.style.transition = 'all 0.6s ease';
                observer.observe(el);
            });
        }
    }

    /**
     * Dark Mode Toggle
     */
    function initDarkMode() {
        const darkModeToggle = document.querySelector('[data-bs-theme-value="dark"]');
        if (!darkModeToggle) return;

        const savedTheme = localStorage.getItem('adminTheme') || 'light';
        applyTheme(savedTheme);

        darkModeToggle.addEventListener('click', function() {
            const currentTheme = localStorage.getItem('adminTheme') || 'light';
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            localStorage.setItem('adminTheme', newTheme);
            applyTheme(newTheme);
        });
    }

    /**
     * Apply Theme
     */
    function applyTheme(theme) {
        const html = document.documentElement;
        if (theme === 'dark') {
            html.setAttribute('data-bs-theme', 'dark');
            document.body.style.backgroundColor = '#1a1a1a';
        } else {
            html.setAttribute('data-bs-theme', 'light');
            document.body.style.backgroundColor = '#fafafa';
        }
    }

    /**
     * Form Enhancements
     */
    window.enhanceForm = function() {
        // Add required field indicator
        const requiredFields = document.querySelectorAll('input[required], textarea[required], select[required]');
        requiredFields.forEach(field => {
            const label = document.querySelector(`label[for="${field.id}"]`);
            if (label && !label.querySelector('.required')) {
                const span = document.createElement('span');
                span.className = 'required';
                span.style.cssText = 'color: red; margin-left: 3px;';
                span.textContent = '*';
                label.appendChild(span);
            }
        });

        // Form validation feedback
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', function(e) {
                if (!form.checkValidity()) {
                    e.preventDefault();
                    e.stopPropagation();
                    showNotification('Please fill all required fields', 'warning');
                }
                form.classList.add('was-validated');
            });
        });
    };

    /**
     * Notification System
     */
    window.showNotification = function(message, type = 'info') {
        const notification = document.createElement('div');
        const bgClass = {
            'success': 'bg-success',
            'error': 'bg-danger',
            'warning': 'bg-warning',
            'info': 'bg-info'
        }[type] || 'bg-info';

        notification.className = `alert alert-dismissible fade show ${bgClass}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            animation: slideInRight 0.3s ease;
        `;
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.remove();
        }, 5000);
    };

    /**
     * Bulk Actions Enhancement
     */
    window.enhanceBulkActions = function() {
        const selectAll = document.querySelector('#action-toggle');
        const actionCheckboxes = document.querySelectorAll('input.action-select');

        if (selectAll) {
            selectAll.addEventListener('change', function() {
                actionCheckboxes.forEach(checkbox => {
                    checkbox.checked = this.checked;
                    checkbox.closest('tr').style.backgroundColor = this.checked ? '#f0f0f0' : '';
                });
            });
        }

        actionCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                this.closest('tr').style.backgroundColor = this.checked ? '#f0f0f0' : '';
                updateBulkActionButton();
            });
        });
    };

    /**
     * Update Bulk Action Button State
     */
    function updateBulkActionButton() {
        const checked = document.querySelectorAll('input.action-select:checked').length;
        const button = document.querySelector('button[name="index"]');
        if (button) {
            button.disabled = checked === 0;
            button.style.opacity = checked === 0 ? '0.5' : '1';
        }
    }

    /**
     * Real-time Stats Update
     */
    window.updateStats = function(selector, value) {
        const element = document.querySelector(selector);
        if (element) {
            element.style.transition = 'all 0.3s ease';
            element.textContent = value;
            element.style.transform = 'scale(1.1)';
            setTimeout(() => {
                element.style.transform = 'scale(1)';
            }, 300);
        }
    };

    /**
     * Export/Import Features
     */
    window.exportData = function(format = 'csv') {
        const table = document.querySelector('#result_list');
        if (!table) return;

        let content = '';
        
        if (format === 'csv') {
            // Export to CSV
            const rows = table.querySelectorAll('tr');
            rows.forEach(row => {
                const cells = row.querySelectorAll('th, td');
                const rowData = Array.from(cells).map(cell => `"${cell.textContent.trim()}"`).join(',');
                content += rowData + '\n';
            });

            downloadFile(content, 'data.csv', 'text/csv');
        }
    };

    /**
     * Download File Helper
     */
    function downloadFile(content, filename, type) {
        const blob = new Blob([content], { type });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    }

    /**
     * Keyboard Shortcuts
     */
    window.initKeyboardShortcuts = function() {
        document.addEventListener('keydown', function(e) {
            // Ctrl+F: Focus search
            if (e.ctrlKey && e.key === 'f') {
                e.preventDefault();
                const searchInput = document.querySelector('#searchbar input');
                if (searchInput) searchInput.focus();
            }

            // Ctrl+S: Submit form
            if (e.ctrlKey && e.key === 's') {
                e.preventDefault();
                const submitBtn = document.querySelector('input[type="submit"]');
                if (submitBtn) submitBtn.click();
            }
        });
    };

    // Export functions for global use
    window.AdminDashboard = {
        enhanceForm,
        showNotification,
        enhanceBulkActions,
        updateStats,
        exportData,
        initKeyboardShortcuts
    };

    // Initialize enhancements
    enhanceForm();
    enhanceBulkActions();
    initKeyboardShortcuts();

})();

/* ========================================================
   CSS ANIMATIONS (Keyframes)
   ======================================================== */

const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(100px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    @keyframes tooltipFade {
        from {
            opacity: 0;
            transform: translateX(-50%) translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateX(-50%) translateY(0);
        }
    }

    mark {
        animation: highlight 0.6s ease;
    }

    @keyframes highlight {
        from {
            background-color: transparent;
        }
        to {
            background-color: #fff59d;
        }
    }
`;
document.head.appendChild(style);
