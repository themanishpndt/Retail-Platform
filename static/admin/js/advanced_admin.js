/* ==================== ADVANCED ADMIN DASHBOARD JAVASCRIPT ==================== */

/**
 * Advanced Admin Dashboard System
 * Provides comprehensive admin functionality with real-time updates,
 * advanced filtering, form handling, and interactive features
 */

class AdvancedAdminDashboard {
    constructor() {
        this.isInitialized = false;
        this.cache = new Map();
        this.listeners = new Map();
        this.config = {
            debounceTime: 300,
            toastDuration: 3000,
            animationDuration: 300,
            maxNotifications: 5,
            apiTimeout: 10000
        };
    }

    /**
     * Initialize all dashboard features
     */
    async init() {
        if (this.isInitialized) return;
        
        try {
            this.initializeHeader();
            this.initializeSidebar();
            this.initializeMainContent();
            this.initializeSearch();
            this.initializeFilters();
            this.initializeForms();
            this.initializeTables();
            this.initializeButtons();
            this.initializeModals();
            this.initializeToasts();
            this.initializeKeyboardShortcuts();
            this.initializeTheme();
            this.loadUserPreferences();
            this.attachGlobalListeners();
            this.startAutoRefresh();
            
            this.isInitialized = true;
            this.notify('Dashboard initialized successfully', 'success');
        } catch (error) {
            console.error('Dashboard initialization error:', error);
            this.notify('Failed to initialize dashboard', 'error');
        }
    }

    /**
     * Initialize header functionality
     */
    initializeHeader() {
        const header = document.getElementById('header');
        if (!header) return;

        // Add search functionality to header
        const searchBox = header.querySelector('.header-search input');
        if (searchBox) {
            this.debounce(searchBox, 'input', (e) => this.globalSearch(e.target.value), this.config.debounceTime);
        }

        // User menu
        const userMenu = header.querySelector('.user-menu');
        if (userMenu) {
            userMenu.addEventListener('click', (e) => {
                e.stopPropagation();
                userMenu.classList.toggle('open');
            });
            document.addEventListener('click', () => userMenu.classList.remove('open'));
        }

        // Theme toggle
        const themeToggle = header.querySelector('.theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleTheme());
        }

        // Notifications badge with real-time update
        this.updateNotificationsBadge();
        setInterval(() => this.updateNotificationsBadge(), 30000);
    }

    /**
     * Initialize sidebar navigation
     */
    initializeSidebar() {
        const sidebar = document.getElementById('sidebar');
        if (!sidebar) return;

        // Mobile toggle
        const sidebarToggle = document.querySelector('.sidebar-toggle');
        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', () => {
                sidebar.classList.toggle('open');
                this.saveUserPreference('sidebarOpen', sidebar.classList.contains('open'));
            });
        }

        // Active state detection
        this.updateActiveSidebarItem();
        window.addEventListener('hashchange', () => this.updateActiveSidebarItem());

        // Search in sidebar
        const sidebarSearch = sidebar.querySelector('.sidebar-search input');
        if (sidebarSearch) {
            this.debounce(sidebarSearch, 'input', (e) => this.filterSidebarItems(e.target.value), 200);
        }

        // Collapse/expand sections
        const sidebarSections = sidebar.querySelectorAll('.sidebar-section > .section-title');
        sidebarSections.forEach(title => {
            title.addEventListener('click', (e) => {
                const section = title.closest('.sidebar-section');
                section.classList.toggle('collapsed');
                this.saveUserPreference('collapsedSections', this.getCollapsedSections());
            });
        });

        // Restore collapsed state
        const collapsedSections = this.getUserPreference('collapsedSections', []);
        collapsedSections.forEach(sectionId => {
            const section = document.getElementById(sectionId);
            if (section) section.classList.add('collapsed');
        });
    }

    /**
     * Initialize main content area
     */
    initializeMainContent() {
        const main = document.getElementById('main');
        if (!main) return;

        // Breadcrumbs
        this.updateBreadcrumbs();

        // Page title
        const pageTitle = main.querySelector('h1, h2');
        if (pageTitle) {
            document.title = pageTitle.textContent + ' - Retail Platform';
        }

        // Action buttons
        const actionButtons = main.querySelectorAll('[data-action]');
        actionButtons.forEach(btn => {
            btn.addEventListener('click', (e) => this.handleActionClick(e));
        });
    }

    /**
     * Initialize advanced search
     */
    initializeSearch() {
        const searchInputs = document.querySelectorAll('[data-search-target]');
        
        searchInputs.forEach(input => {
            this.debounce(input, 'input', (e) => {
                const target = document.getElementById(input.dataset.searchTarget);
                if (target) {
                    this.searchInElement(e.target.value, target);
                }
            }, this.config.debounceTime);

            // Autocomplete
            if (input.dataset.autocomplete) {
                this.initializeAutocomplete(input);
            }
        });

        // Search with highlighting
        this.highlightSearchTerms();
    }

    /**
     * Initialize advanced filters
     */
    initializeFilters() {
        const filterElements = document.querySelectorAll('[data-filter]');
        
        filterElements.forEach(filter => {
            filter.addEventListener('change', (e) => {
                this.applyFilters();
                this.saveUserPreference('activeFilters', this.getActiveFilters());
            });
        });

        // Restore previous filters
        const savedFilters = this.getUserPreference('activeFilters', {});
        Object.entries(savedFilters).forEach(([key, value]) => {
            const filter = document.querySelector(`[data-filter="${key}"]`);
            if (filter) filter.value = value;
        });

        // Filter chips
        this.updateFilterChips();

        // Clear filters button
        const clearBtn = document.querySelector('.clear-filters');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearAllFilters());
        }
    }

    /**
     * Initialize advanced form functionality
     */
    initializeForms() {
        const forms = document.querySelectorAll('form[data-enhanced]');
        
        forms.forEach(form => {
            // Required field indicators
            this.addRequiredFieldIndicators(form);

            // Form validation
            form.addEventListener('submit', (e) => this.validateForm(e, form));

            // Field changes tracking
            this.trackFormChanges(form);

            // Auto-save drafts
            if (form.dataset.autoSave === 'true') {
                this.enableFormAutosave(form);
            }

            // Field dependencies
            this.setupFieldDependencies(form);

            // Keyboard shortcuts
            form.addEventListener('keydown', (e) => {
                if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                    e.preventDefault();
                    form.submit();
                }
            });
        });

        // Textarea auto-expand
        document.querySelectorAll('textarea[data-auto-expand]').forEach(textarea => {
            textarea.addEventListener('input', () => this.autoExpandTextarea(textarea));
        });

        // Date pickers
        document.querySelectorAll('input[type="date"]').forEach(input => {
            input.addEventListener('change', () => this.updateDateRelated(input));
        });
    }

    /**
     * Initialize table functionality
     */
    initializeTables() {
        const tables = document.querySelectorAll('table[data-enhanced]');
        
        tables.forEach(table => {
            // Column sorting
            const headers = table.querySelectorAll('thead th');
            headers.forEach((th, index) => {
                th.style.cursor = 'pointer';
                th.addEventListener('click', () => this.sortTable(table, index));
            });

            // Row selection
            this.initializeRowSelection(table);

            // Row highlighting
            const rows = table.querySelectorAll('tbody tr');
            rows.forEach(row => {
                row.addEventListener('click', (e) => {
                    if (!e.target.closest('input[type="checkbox"]')) {
                        row.classList.toggle('selected');
                    }
                });
            });

            // Bulk actions
            this.initializeBulkActions(table);

            // Inline editing
            if (table.dataset.inlineEdit === 'true') {
                this.enableInlineEditing(table);
            }

            // Pagination
            this.initializePagination(table);

            // Export
            const exportBtn = table.closest('.table-container').querySelector('[data-export]');
            if (exportBtn) {
                exportBtn.addEventListener('click', () => this.exportTable(table));
            }
        });
    }

    /**
     * Initialize button functionality
     */
    initializeButtons() {
        // Action buttons
        document.querySelectorAll('button[data-confirm]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                this.showConfirmDialog(btn.dataset.confirm, () => {
                    this.handleButtonAction(btn);
                });
            });
        });

        // Loading state buttons
        document.querySelectorAll('button[data-loading]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                btn.disabled = true;
                btn.dataset.originalText = btn.textContent;
                btn.innerHTML = '<span class="spinner"></span> Processing...';
                
                // Re-enable after 2 seconds or when action completes
                setTimeout(() => {
                    btn.disabled = false;
                    btn.textContent = btn.dataset.originalText;
                }, 2000);
            });
        });

        // Tooltip buttons
        document.querySelectorAll('button[data-tooltip]').forEach(btn => {
            btn.addEventListener('mouseenter', (e) => {
                this.showTooltip(btn, btn.dataset.tooltip);
            });
            btn.addEventListener('mouseleave', () => {
                this.hideTooltips();
            });
        });
    }

    /**
     * Initialize modals
     */
    initializeModals() {
        const modals = document.querySelectorAll('.modal[data-modal]');
        
        modals.forEach(modal => {
            // Close button
            const closeBtn = modal.querySelector('.close-btn');
            if (closeBtn) {
                closeBtn.addEventListener('click', () => this.closeModal(modal));
            }

            // Outside click to close
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal(modal);
                }
            });

            // Escape key to close
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && modal.classList.contains('open')) {
                    this.closeModal(modal);
                }
            });
        });

        // Open modal buttons
        document.querySelectorAll('[data-modal-trigger]').forEach(btn => {
            btn.addEventListener('click', () => {
                const modalId = btn.dataset.modalTrigger;
                this.openModal(document.getElementById(modalId));
            });
        });
    }

    /**
     * Initialize toast notifications
     */
    initializeToasts() {
        // Toast container
        if (!document.getElementById('toast-container')) {
            const container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container';
            document.body.appendChild(container);
        }

        // Auto-dismiss alerts
        document.querySelectorAll('.alert').forEach(alert => {
            if (alert.dataset.autoDismiss) {
                setTimeout(() => {
                    alert.style.animation = 'slideOut 0.3s ease-out';
                    setTimeout(() => alert.remove(), 300);
                }, parseInt(alert.dataset.autoDismiss));
            }
        });
    }

    /**
     * Initialize keyboard shortcuts
     */
    initializeKeyboardShortcuts() {
        const shortcuts = {
            'Ctrl+F': () => {
                const searchInput = document.querySelector('[data-search-target]');
                if (searchInput) searchInput.focus();
            },
            'Ctrl+S': () => {
                const form = document.querySelector('form:invalid');
                if (form) form.submit();
            },
            'Ctrl+N': () => {
                const addBtn = document.querySelector('[data-action="add"]');
                if (addBtn) addBtn.click();
            },
            'Escape': () => {
                const modal = document.querySelector('.modal.open');
                if (modal) this.closeModal(modal);
            }
        };

        document.addEventListener('keydown', (e) => {
            const combination = `${e.ctrlKey ? 'Ctrl+' : ''}${e.metaKey ? 'Cmd+' : ''}${e.key === ' ' ? 'Space' : e.key}`;
            if (shortcuts[combination]) {
                e.preventDefault();
                shortcuts[combination]();
            }
        });
    }

    /**
     * Initialize theme switching
     */
    initializeTheme() {
        const savedTheme = this.getUserPreference('theme', 'light');
        this.setTheme(savedTheme);
    }

    /**
     * UTILITY METHODS
     */

    /**
     * Debounce function for performance
     */
    debounce(element, event, callback, delay) {
        let timeout;
        element.addEventListener(event, function(e) {
            clearTimeout(timeout);
            timeout = setTimeout(() => callback.call(this, e), delay);
        });
    }

    /**
     * Global search functionality
     */
    globalSearch(query) {
        if (!query) {
            this.resetSearch();
            return;
        }

        const elements = document.querySelectorAll('[data-searchable]');
        let foundCount = 0;

        elements.forEach(element => {
            const text = element.textContent.toLowerCase();
            if (text.includes(query.toLowerCase())) {
                element.classList.remove('hidden');
                this.highlightText(element, query);
                foundCount++;
            } else {
                element.classList.add('hidden');
            }
        });

        this.updateSearchStats(foundCount, query);
    }

    /**
     * Filter sidebar items
     */
    filterSidebarItems(query) {
        const items = document.querySelectorAll('#sidebar a');
        let visibleCount = 0;

        items.forEach(item => {
            const text = item.textContent.toLowerCase();
            if (text.includes(query.toLowerCase())) {
                item.closest('li').classList.remove('hidden');
                visibleCount++;
            } else {
                item.closest('li').classList.add('hidden');
            }
        });

        return visibleCount;
    }

    /**
     * Apply all active filters
     */
    applyFilters() {
        const filters = this.getActiveFilters();
        const items = document.querySelectorAll('[data-filterable]');

        items.forEach(item => {
            let isVisible = true;

            Object.entries(filters).forEach(([filterName, filterValue]) => {
                const itemValue = item.dataset[filterName];
                if (itemValue && !itemValue.includes(filterValue)) {
                    isVisible = false;
                }
            });

            item.classList.toggle('hidden', !isVisible);
        });

        this.updateFilterChips();
    }

    /**
     * Clear all filters
     */
    clearAllFilters() {
        document.querySelectorAll('[data-filter]').forEach(filter => {
            filter.value = '';
        });
        this.applyFilters();
        this.saveUserPreference('activeFilters', {});
    }

    /**
     * Get active filters
     */
    getActiveFilters() {
        const filters = {};
        document.querySelectorAll('[data-filter]').forEach(filter => {
            if (filter.value) {
                filters[filter.dataset.filter] = filter.value;
            }
        });
        return filters;
    }

    /**
     * Update filter chips display
     */
    updateFilterChips() {
        const container = document.querySelector('.filter-chips');
        if (!container) return;

        container.innerHTML = '';
        const filters = this.getActiveFilters();

        Object.entries(filters).forEach(([key, value]) => {
            const chip = document.createElement('span');
            chip.className = 'filter-chip';
            chip.innerHTML = `${key}: ${value} <button data-remove-filter="${key}" class="remove-chip">×</button>`;
            container.appendChild(chip);

            chip.querySelector('[data-remove-filter]').addEventListener('click', () => {
                const filter = document.querySelector(`[data-filter="${key}"]`);
                if (filter) filter.value = '';
                this.applyFilters();
            });
        });
    }

    /**
     * Add required field indicators
     */
    addRequiredFieldIndicators(form) {
        form.querySelectorAll('[required]').forEach(field => {
            const label = form.querySelector(`label[for="${field.id}"]`);
            if (label && !label.querySelector('.required-indicator')) {
                const indicator = document.createElement('span');
                indicator.className = 'required-indicator';
                indicator.textContent = ' *';
                label.appendChild(indicator);
            }
        });
    }

    /**
     * Validate form
     */
    validateForm(e, form) {
        let isValid = true;
        const errors = [];

        form.querySelectorAll('[required]').forEach(field => {
            if (!field.value.trim()) {
                isValid = false;
                errors.push(`${field.name} is required`);
                field.classList.add('error');
            } else {
                field.classList.remove('error');
            }
        });

        form.querySelectorAll('[data-validate]').forEach(field => {
            const validator = field.dataset.validate;
            if (!this.validateField(field, validator)) {
                isValid = false;
                errors.push(`${field.name} is invalid`);
                field.classList.add('error');
            }
        });

        if (!isValid) {
            e.preventDefault();
            this.notify(errors.join(', '), 'error');
        }

        return isValid;
    }

    /**
     * Validate individual field
     */
    validateField(field, validator) {
        const value = field.value;
        const validators = {
            'email': /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
            'phone': /^\d{10,}$/,
            'number': /^\d+$/,
            'url': /^https?:\/\/.+/,
            'date': /^\d{4}-\d{2}-\d{2}$/
        };

        if (validators[validator]) {
            return validators[validator].test(value);
        }
        return true;
    }

    /**
     * Track form changes for unsaved warnings
     */
    trackFormChanges(form) {
        let isModified = false;
        const originalData = new FormData(form);

        form.querySelectorAll('input, textarea, select').forEach(field => {
            field.addEventListener('change', () => {
                isModified = true;
                form.classList.add('modified');
            });
        });

        window.addEventListener('beforeunload', (e) => {
            if (isModified) {
                e.preventDefault();
                e.returnValue = '';
            }
        });

        form.addEventListener('submit', () => {
            isModified = false;
            form.classList.remove('modified');
        });
    }

    /**
     * Enable form autosave
     */
    enableFormAutosave(form) {
        setInterval(() => {
            if (form.classList.contains('modified')) {
                const formData = new FormData(form);
                this.saveFormDraft(form.id, Object.fromEntries(formData));
                this.notify('Draft saved', 'info');
            }
        }, 30000); // Save every 30 seconds
    }

    /**
     * Setup field dependencies
     */
    setupFieldDependencies(form) {
        form.querySelectorAll('[data-depends-on]').forEach(field => {
            const dependsOn = field.dataset.dependsOn.split(',');
            dependsOn.forEach(depField => {
                const trigger = form.querySelector(`[name="${depField}"]`);
                if (trigger) {
                    trigger.addEventListener('change', () => {
                        this.updateFieldDependencies(form, field);
                    });
                }
            });
        });
    }

    /**
     * Auto-expand textarea
     */
    autoExpandTextarea(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = (textarea.scrollHeight) + 'px';
    }

    /**
     * Sort table
     */
    sortTable(table, columnIndex) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        
        const isAscending = table.dataset.sortColumn === String(columnIndex) && 
                           table.dataset.sortOrder === 'asc';
        
        rows.sort((a, b) => {
            const aValue = a.cells[columnIndex].textContent;
            const bValue = b.cells[columnIndex].textContent;
            
            const compareResult = isNaN(aValue) 
                ? aValue.localeCompare(bValue)
                : parseFloat(aValue) - parseFloat(bValue);
            
            return isAscending ? -compareResult : compareResult;
        });

        rows.forEach(row => tbody.appendChild(row));
        
        table.dataset.sortColumn = columnIndex;
        table.dataset.sortOrder = isAscending ? 'desc' : 'asc';

        // Update visual indicator
        table.querySelectorAll('th').forEach((th, index) => {
            th.classList.remove('sort-asc', 'sort-desc');
            if (index === columnIndex) {
                th.classList.add(isAscending ? 'sort-desc' : 'sort-asc');
            }
        });
    }

    /**
     * Initialize row selection in tables
     */
    initializeRowSelection(table) {
        const selectAllCheckbox = table.querySelector('thead input[type="checkbox"]');
        const rowCheckboxes = table.querySelectorAll('tbody input[type="checkbox"]');

        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', (e) => {
                rowCheckboxes.forEach(checkbox => {
                    checkbox.checked = e.target.checked;
                });
                this.updateBulkActionButtons(table);
            });
        }

        rowCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                this.updateBulkActionButtons(table);
            });
        });
    }

    /**
     * Initialize bulk actions
     */
    initializeBulkActions(table) {
        const bulkActionBtn = table.querySelector('[data-bulk-action]');
        if (bulkActionBtn) {
            bulkActionBtn.addEventListener('click', () => {
                const selectedRows = this.getSelectedRows(table);
                if (selectedRows.length === 0) {
                    this.notify('Please select at least one item', 'warning');
                    return;
                }
                this.performBulkAction(table, selectedRows);
            });
        }
    }

    /**
     * Get selected rows
     */
    getSelectedRows(table) {
        const checkboxes = table.querySelectorAll('tbody input[type="checkbox"]:checked');
        return Array.from(checkboxes).map(checkbox => checkbox.closest('tr'));
    }

    /**
     * Update bulk action buttons visibility
     */
    updateBulkActionButtons(table) {
        const selectedCount = table.querySelectorAll('tbody input[type="checkbox"]:checked').length;
        const bulkActionsBar = table.querySelector('.bulk-actions-bar');
        if (bulkActionsBar) {
            bulkActionsBar.classList.toggle('hidden', selectedCount === 0);
            bulkActionsBar.querySelector('[data-selected-count]').textContent = selectedCount;
        }
    }

    /**
     * Perform bulk action
     */
    performBulkAction(table, selectedRows) {
        const actionSelect = table.querySelector('[data-bulk-action-select]');
        const action = actionSelect.value;

        if (!action) {
            this.notify('Please select an action', 'warning');
            return;
        }

        this.showConfirmDialog(`Are you sure you want to ${action} these ${selectedRows.length} items?`, () => {
            // Send request to server
            console.log(`Performing ${action} on ${selectedRows.length} rows`);
            this.notify(`Action "${action}" performed successfully`, 'success');
        });
    }

    /**
     * Initialize pagination
     */
    initializePagination(table) {
        const pagination = table.querySelector('.pagination');
        if (!pagination) return;

        const pageLinks = pagination.querySelectorAll('a');
        pageLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                this.loadPage(link.href);
            });
        });
    }

    /**
     * Export table to CSV
     */
    exportTable(table) {
        let csv = [];
        const rows = table.querySelectorAll('tr');

        rows.forEach(row => {
            const cols = row.querySelectorAll('td, th');
            let csvRow = [];
            cols.forEach(col => {
                csvRow.push(`"${col.textContent.trim()}"`);
            });
            csv.push(csvRow.join(','));
        });

        const csvContent = 'data:text/csv;charset=utf-8,' + csv.join('\n');
        const link = document.createElement('a');
        link.setAttribute('href', encodeURI(csvContent));
        link.setAttribute('download', `export_${new Date().getTime()}.csv`);
        link.click();

        this.notify('Table exported successfully', 'success');
    }

    /**
     * Show toast notification
     */
    notify(message, type = 'info') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast toast-${type} animate-slide-in-left`;
        toast.innerHTML = `
            <span class="toast-icon">${this.getIcon(type)}</span>
            <span class="toast-message">${message}</span>
            <button class="toast-close">&times;</button>
        `;

        container.appendChild(toast);

        const closeBtn = toast.querySelector('.toast-close');
        closeBtn.addEventListener('click', () => {
            toast.remove();
        });

        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => toast.remove(), 300);
        }, this.config.toastDuration);
    }

    /**
     * Show confirmation dialog
     */
    showConfirmDialog(message, onConfirm) {
        const modal = document.createElement('div');
        modal.className = 'modal modal-confirm open';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Confirm Action</h3>
                    <button class="close-btn">&times;</button>
                </div>
                <div class="modal-body">
                    <p>${message}</p>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary cancel-btn">Cancel</button>
                    <button class="btn btn-danger confirm-btn">Confirm</button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        const confirmBtn = modal.querySelector('.confirm-btn');
        const cancelBtn = modal.querySelector('.cancel-btn');
        const closeBtn = modal.querySelector('.close-btn');

        const handleClose = () => modal.remove();

        confirmBtn.addEventListener('click', () => {
            onConfirm();
            handleClose();
        });

        cancelBtn.addEventListener('click', handleClose);
        closeBtn.addEventListener('click', handleClose);

        modal.addEventListener('click', (e) => {
            if (e.target === modal) handleClose();
        });
    }

    /**
     * Open modal
     */
    openModal(modal) {
        if (!modal) return;
        modal.classList.add('open');
        document.body.style.overflow = 'hidden';
    }

    /**
     * Close modal
     */
    closeModal(modal) {
        if (!modal) return;
        modal.classList.remove('open');
        document.body.style.overflow = '';
    }

    /**
     * Toggle theme
     */
    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        this.setTheme(newTheme);
        this.saveUserPreference('theme', newTheme);
    }

    /**
     * Set theme
     */
    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        const icon = document.querySelector('.theme-toggle i');
        if (icon) {
            icon.className = theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
        }
    }

    /**
     * User preferences management
     */
    saveUserPreference(key, value) {
        const prefs = JSON.parse(localStorage.getItem('adminPrefs') || '{}');
        prefs[key] = value;
        localStorage.setItem('adminPrefs', JSON.stringify(prefs));
    }

    getUserPreference(key, defaultValue) {
        const prefs = JSON.parse(localStorage.getItem('adminPrefs') || '{}');
        return prefs[key] !== undefined ? prefs[key] : defaultValue;
    }

    loadUserPreferences() {
        const sidebarOpen = this.getUserPreference('sidebarOpen', true);
        const sidebar = document.getElementById('sidebar');
        if (sidebar && !sidebarOpen) {
            sidebar.classList.remove('open');
        }
    }

    /**
     * Get icon based on type
     */
    getIcon(type) {
        const icons = {
            'success': '✓',
            'error': '✕',
            'warning': '⚠',
            'info': 'ℹ'
        };
        return icons[type] || 'ℹ';
    }

    /**
     * Highlight text in element
     */
    highlightText(element, text) {
        const regex = new RegExp(`(${text})`, 'gi');
        element.innerHTML = element.innerHTML.replace(regex, '<mark>$1</mark>');
    }

    /**
     * Update active sidebar item
     */
    updateActiveSidebarItem() {
        const currentUrl = window.location.pathname;
        document.querySelectorAll('#sidebar a').forEach(link => {
            const href = link.getAttribute('href');
            if (href && currentUrl.includes(href)) {
                link.closest('li').classList.add('selected');
                link.closest('li').siblings().forEach(sibling => sibling.classList.remove('selected'));
            } else {
                link.closest('li').classList.remove('selected');
            }
        });
    }

    /**
     * Update breadcrumbs
     */
    updateBreadcrumbs() {
        const pathSegments = window.location.pathname.split('/').filter(seg => seg);
        const breadcrumbs = document.querySelector('.breadcrumbs');
        if (!breadcrumbs) return;

        let html = '<a href="/">Home</a>';
        let path = '';

        pathSegments.forEach(segment => {
            path += '/' + segment;
            html += ` / <a href="${path}">${segment}</a>`;
        });

        breadcrumbs.innerHTML = html;
    }

    /**
     * Utility: Get collapsed sections
     */
    getCollapsedSections() {
        const collapsed = [];
        document.querySelectorAll('.sidebar-section.collapsed').forEach(section => {
            if (section.id) collapsed.push(section.id);
        });
        return collapsed;
    }

    /**
     * Update notifications badge
     */
    updateNotificationsBadge() {
        const badge = document.querySelector('[data-notifications-badge]');
        if (badge) {
            // Fetch notification count from server
            fetch('/api/notifications/count')
                .then(r => r.json())
                .then(data => {
                    badge.textContent = data.count;
                    badge.style.display = data.count > 0 ? 'block' : 'none';
                })
                .catch(err => console.error('Notification error:', err));
        }
    }

    /**
     * Start auto-refresh for live data
     */
    startAutoRefresh() {
        setInterval(() => {
            if (document.querySelector('[data-auto-refresh]')) {
                this.refreshDashboard();
            }
        }, 60000); // Refresh every minute
    }

    /**
     * Refresh dashboard data
     */
    refreshDashboard() {
        // Implement dashboard refresh logic
    }

    /**
     * Save form draft
     */
    saveFormDraft(formId, data) {
        const drafts = JSON.parse(sessionStorage.getItem('formDrafts') || '{}');
        drafts[formId] = {data, timestamp: Date.now()};
        sessionStorage.setItem('formDrafts', JSON.stringify(drafts));
    }

    /**
     * Show tooltip
     */
    showTooltip(element, text) {
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = text;
        document.body.appendChild(tooltip);

        const rect = element.getBoundingClientRect();
        tooltip.style.top = (rect.top - tooltip.offsetHeight - 10) + 'px';
        tooltip.style.left = (rect.left + rect.width / 2 - tooltip.offsetWidth / 2) + 'px';
    }

    /**
     * Hide tooltips
     */
    hideTooltips() {
        document.querySelectorAll('.tooltip').forEach(tooltip => tooltip.remove());
    }

    /**
     * Handle action click
     */
    handleActionClick(e) {
        const action = e.target.dataset.action;
        console.log('Action:', action);
    }

    /**
     * Handle button action
     */
    handleButtonAction(button) {
        const action = button.dataset.confirm;
        // Implement action
        console.log('Executing action:', action);
    }

    /**
     * Search in element
     */
    searchInElement(query, target) {
        // Implement element search
    }

    /**
     * Highlight search terms
     */
    highlightSearchTerms() {
        // Implement search highlighting
    }

    /**
     * Update search stats
     */
    updateSearchStats(count, query) {
        console.log(`Found ${count} results for "${query}"`);
    }

    /**
     * Reset search
     */
    resetSearch() {
        document.querySelectorAll('[data-searchable]').forEach(el => {
            el.classList.remove('hidden');
        });
    }

    /**
     * Initialize autocomplete
     */
    initializeAutocomplete(input) {
        // Implement autocomplete
    }

    /**
     * Update date related fields
     */
    updateDateRelated(input) {
        // Implement date-related updates
    }

    /**
     * Update field dependencies
     */
    updateFieldDependencies(form, field) {
        // Implement field dependency logic
    }

    /**
     * Enable inline editing
     */
    enableInlineEditing(table) {
        // Implement inline editing
    }

    /**
     * Load page
     */
    loadPage(url) {
        // Implement page loading
    }

    /**
     * Attach global event listeners
     */
    attachGlobalListeners() {
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('external-link')) {
                window.open(e.target.href, '_blank');
            }
        });
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const dashboard = new AdvancedAdminDashboard();
    dashboard.init();
    window.AdminDashboard = dashboard;
});

// Make dashboard available globally
window.AdvancedAdminDashboard = AdvancedAdminDashboard;
