// Global Application State
const AppState = {
    selectedApp: "",
    selectedLocale: "",
    selectedMonthA: "", // Base month (can be empty)
    selectedMonthB: "", // Target month
    
    // Dropdown lists
    apps: [],
    locales: [],
    months: [],
    
    // Cached API response data
    overviewData: null,
    keywordsData: null,
    moversData: null,
    setupData: null,
    
    // Tab tracking
    activeTab: "overview", // 'overview', 'setup', 'keywords', 'trends', 'movers'
};

// DOM Elements
const elements = {
    selectApp: document.getElementById("select-app"),
    selectLocale: document.getElementById("select-locale"),
    selectMonthA: document.getElementById("select-month-a"),
    selectMonthB: document.getElementById("select-month-b"),
    btnRefresh: document.getElementById("btn-refresh"),
    btnExport: document.getElementById("btn-export"),
    loader: document.getElementById("loader"),
    emptyState: document.getElementById("empty-state"),
    tabContent: document.getElementById("tab-content"),
    tabs: document.querySelectorAll(".tab-item"),
    tabPanes: document.querySelectorAll(".tab-pane"),
    toast: document.getElementById("toast")
};

// Initialize Application
document.addEventListener("DOMContentLoaded", () => {
    initEventListeners();
    fetchApps();
});

// Event Listeners Registration
function initEventListeners() {
    // Dropdowns
    elements.selectApp.addEventListener("change", (e) => {
        AppState.selectedApp = e.target.value;
        AppState.selectedLocale = "";
        AppState.selectedMonthA = "";
        AppState.selectedMonthB = "";
        AppState.setupData = null;
        resetDropdowns(["locale", "month-a", "month-b"]);
        fetchLocales(AppState.selectedApp);
        fetchSetup(AppState.selectedApp);
    });

    elements.selectLocale.addEventListener("change", (e) => {
        AppState.selectedLocale = e.target.value;
        AppState.selectedMonthA = "";
        AppState.selectedMonthB = "";
        resetDropdowns(["month-a", "month-b"]);
        fetchMonths(AppState.selectedApp, AppState.selectedLocale);
    });

    elements.selectMonthA.addEventListener("change", (e) => {
        AppState.selectedMonthA = e.target.value;
        handleSelectionChange();
    });

    elements.selectMonthB.addEventListener("change", (e) => {
        AppState.selectedMonthB = e.target.value;
        handleSelectionChange();
    });

    // Refresh Data
    elements.btnRefresh.addEventListener("click", triggerRefresh);

    // Export Excel
    elements.btnExport.addEventListener("click", triggerExport);

    // Tab Navigation
    elements.tabs.forEach(tab => {
        tab.addEventListener("click", () => {
            const targetTab = tab.getAttribute("data-tab");
            switchTab(targetTab);
        });
    });
}

// Reset Dropdowns Helper
function resetDropdowns(types) {
    if (types.includes("locale")) {
        elements.selectLocale.innerHTML = '<option value="" disabled selected>Select Locale</option>';
        elements.selectLocale.disabled = true;
    }
    if (types.includes("month-a")) {
        elements.selectMonthA.innerHTML = '<option value="">None (Single Month)</option>';
        elements.selectMonthA.disabled = true;
    }
    if (types.includes("month-b")) {
        elements.selectMonthB.innerHTML = '<option value="" disabled selected>Select Month B</option>';
        elements.selectMonthB.disabled = true;
    }
    
    // Disable export
    elements.btnExport.disabled = true;
    
    // Hide content
    if (AppState.activeTab !== "setup" || !AppState.selectedApp) {
        elements.tabContent.classList.add("hidden");
        elements.emptyState.classList.remove("hidden");
    }
}

// Show/Hide Loader
function showLoader(show) {
    if (show) {
        elements.loader.classList.remove("hidden");
    } else {
        elements.loader.classList.add("hidden");
    }
}

// Toast Notification
let toastTimeout;
function showToast(message, type = "success") {
    clearTimeout(toastTimeout);
    elements.toast.textContent = message;
    elements.toast.className = "toast"; // Reset class
    if (type !== "success") {
        elements.toast.classList.add(type);
    }
    elements.toast.classList.remove("hidden");
    
    toastTimeout = setTimeout(() => {
        elements.toast.classList.add("hidden");
    }, 3000);
}

// Tab Switching Logic
function switchTab(tabName) {
    if (AppState.activeTab === tabName) return;
    
    // Update active tab class
    elements.tabs.forEach(tab => {
        if (tab.getAttribute("data-tab") === tabName) {
            tab.classList.add("active");
        } else {
            tab.classList.remove("active");
        }
    });

    // Update active tab pane
    elements.tabPanes.forEach(pane => {
        if (pane.id === `content-${tabName}`) {
            pane.classList.add("active");
        } else {
            pane.classList.remove("active");
        }
    });

    AppState.activeTab = tabName;
    
    // Render the active tab content if we have data loaded
    if (tabName === "setup" && AppState.selectedApp) {
        elements.emptyState.classList.add("hidden");
        elements.tabContent.classList.remove("hidden");
        if (AppState.setupData) {
            renderActiveTab();
        } else {
            fetchSetup(AppState.selectedApp);
        }
    } else if (AppState.keywordsData) {
        renderActiveTab();
    } else {
        elements.tabContent.classList.add("hidden");
        elements.emptyState.classList.remove("hidden");
    }
}

// API Calls
async function fetchApps() {
    showLoader(true);
    try {
        const response = await fetch("/api/apps");
        const result = await response.json();
        if (result.success) {
            AppState.apps = result.apps;
            
            // Populate select options
            elements.selectApp.innerHTML = '<option value="" disabled selected>Select App</option>';
            AppState.apps.forEach(app => {
                const opt = document.createElement("option");
                opt.value = app;
                opt.textContent = app.replace(/_/g, " ");
                elements.selectApp.appendChild(opt);
            });
            
            elements.selectApp.disabled = false;
        } else {
            showToast("Failed to fetch apps: " + result.error, "danger");
        }
    } catch (e) {
        showToast("Error loading apps: " + e.message, "danger");
    } finally {
        showLoader(false);
    }
}

async function fetchLocales(appName) {
    showLoader(true);
    try {
        const response = await fetch(`/api/locales/${appName}`);
        const result = await response.json();
        if (result.success) {
            AppState.locales = result.locales;
            
            elements.selectLocale.innerHTML = '<option value="" disabled selected>Select Locale</option>';
            AppState.locales.forEach(loc => {
                const opt = document.createElement("option");
                opt.value = loc;
                opt.textContent = loc;
                elements.selectLocale.appendChild(opt);
            });
            
            elements.selectLocale.disabled = false;
        } else {
            showToast("Failed to fetch locales: " + result.error, "danger");
        }
    } catch (e) {
        showToast("Error loading locales: " + e.message, "danger");
    } finally {
        showLoader(false);
    }
}

async function fetchMonths(appName, locale) {
    showLoader(true);
    try {
        const response = await fetch(`/api/months/${appName}/${locale}`);
        const result = await response.json();
        if (result.success) {
            AppState.months = result.months;
            
            // Populating Month B (Target)
            elements.selectMonthB.innerHTML = '<option value="" disabled selected>Select Month B</option>';
            AppState.months.forEach(m => {
                const opt = document.createElement("option");
                opt.value = m;
                opt.textContent = formatMonthString(m);
                elements.selectMonthB.appendChild(opt);
            });
            
            // Populating Month A (Base)
            elements.selectMonthA.innerHTML = '<option value="">None (Single Month)</option>';
            AppState.months.forEach(m => {
                const opt = document.createElement("option");
                opt.value = m;
                opt.textContent = formatMonthString(m);
                elements.selectMonthA.appendChild(opt);
            });
            
            elements.selectMonthB.disabled = false;
            elements.selectMonthA.disabled = false;
            
            // Handle smart defaults
            if (AppState.months.length > 0) {
                // Month B defaults to latest month
                const latestMonth = AppState.months[AppState.months.length - 1];
                elements.selectMonthB.value = latestMonth;
                AppState.selectedMonthB = latestMonth;
                
                if (AppState.months.length > 1) {
                    // Month A defaults to second latest month
                    const secondLatestMonth = AppState.months[AppState.months.length - 2];
                    elements.selectMonthA.value = secondLatestMonth;
                    AppState.selectedMonthA = secondLatestMonth;
                } else {
                    elements.selectMonthA.value = "";
                    AppState.selectedMonthA = "";
                }
                
                handleSelectionChange();
            }
        } else {
            showToast("Failed to fetch months: " + result.error, "danger");
        }
    } catch (e) {
        showToast("Error loading months: " + e.message, "danger");
    } finally {
        showLoader(false);
    }
}

async function fetchSetup(appName) {
    if (!appName) return;
    try {
        const response = await fetch(`/api/setup/${appName}`);
        const result = await response.json();
        if (result.success) {
            AppState.setupData = result.data;
            if (AppState.activeTab === "setup") {
                elements.emptyState.classList.add("hidden");
                elements.tabContent.classList.remove("hidden");
                renderActiveTab();
            }
        } else {
            showToast("Failed to fetch setup: " + result.error, "danger");
        }
    } catch (e) {
        showToast("Error loading setup: " + e.message, "danger");
    }
}

// Trigger selection changes (App, Locale, Month A, Month B selected)
async function handleSelectionChange() {
    if (!AppState.selectedApp || !AppState.selectedLocale || !AppState.selectedMonthB) {
        resetDropdowns([]); // Just clear selections and views
        return;
    }
    
    // Enable export button
    elements.btnExport.disabled = false;
    
    // Show content layout
    elements.emptyState.classList.add("hidden");
    elements.tabContent.classList.remove("hidden");
    
    showLoader(true);
    
    // Fetch tab data in parallel for smooth instantaneous transitions
    try {
        const [overviewRes, keywordsRes, moversRes, setupRes] = await Promise.all([
            fetch(`/api/overview/${AppState.selectedApp}/${AppState.selectedLocale}`),
            fetch(`/api/keywords/${AppState.selectedApp}/${AppState.selectedLocale}?month_a=${AppState.selectedMonthA}&month_b=${AppState.selectedMonthB}`),
            fetch(`/api/movers/${AppState.selectedApp}/${AppState.selectedLocale}?month_a=${AppState.selectedMonthA}&month_b=${AppState.selectedMonthB}`),
            AppState.setupData ? Promise.resolve(null) : fetch(`/api/setup/${AppState.selectedApp}`)
        ]);
        
        const overviewResult = await overviewRes.json();
        const keywordsResult = await keywordsRes.json();
        const moversResult = await moversRes.json();
        const setupResult = setupRes ? await setupRes.json() : { success: true, data: AppState.setupData };
        
        if (overviewResult.success && keywordsResult.success && moversResult.success && setupResult.success) {
            AppState.overviewData = overviewResult.data;
            AppState.keywordsData = keywordsResult.data;
            AppState.moversData = moversResult.data;
            AppState.setupData = setupResult.data;
            
            // Render the active tab
            renderActiveTab();
        } else {
            showToast("Failed to fetch API data", "danger");
        }
    } catch (e) {
        showToast("Error fetching dashboard data: " + e.message, "danger");
    } finally {
        showLoader(false);
    }
}

// Render active tab template
function renderActiveTab() {
    // Notify window components to resize their charts
    setTimeout(() => {
        window.dispatchEvent(new Event('resize'));
    }, 100);

    switch (AppState.activeTab) {
        case "overview":
            if (typeof renderOverviewTab === "function") {
                renderOverviewTab(AppState.overviewData, AppState.selectedMonthA, AppState.selectedMonthB);
            }
            break;
        case "setup":
            if (typeof renderSetupTab === "function") {
                renderSetupTab(AppState.setupData);
            }
            break;
        case "keywords":
            if (typeof renderKeywordsTab === "function") {
                renderKeywordsTab(AppState.keywordsData);
            }
            break;
        case "trends":
            if (typeof renderTrendsTab === "function") {
                renderTrendsTab(AppState.keywordsData);
            }
            break;
        case "movers":
            if (typeof renderMoversTab === "function") {
                renderMoversTab(AppState.moversData);
            }
            break;
    }
}

// Refresh logic
async function triggerRefresh() {
    showLoader(true);
    try {
        const response = await fetch("/api/refresh", { method: "POST" });
        const result = await response.json();
        if (result.success) {
            const files = result.files_imported;
            const rows = result.rows_imported;
            showToast(`Refreshed! Imported ${files} new files (${rows} rows).`);
            
            // Cache current state
            const currentApp = AppState.selectedApp;
            const currentLocale = AppState.selectedLocale;
            
            // Reload apps list
            await fetchApps();
            
            // Restore selection if they still exist
            if (currentApp && AppState.apps.includes(currentApp)) {
                elements.selectApp.value = currentApp;
                AppState.selectedApp = currentApp;
                
                await fetchLocales(currentApp);
                if (currentLocale && AppState.locales.includes(currentLocale)) {
                    elements.selectLocale.value = currentLocale;
                    AppState.selectedLocale = currentLocale;
                    
                    await fetchMonths(currentApp, currentLocale);
                }
            }
        } else {
            showToast("Refresh failed: " + result.error, "danger");
        }
    } catch (e) {
        showToast("Error during refresh: " + e.message, "danger");
    } finally {
        showLoader(false);
    }
}

// Export excel report
function triggerExport() {
    if (!AppState.selectedApp || !AppState.selectedLocale || !AppState.selectedMonthB) return;
    
    const url = `/api/export/${AppState.selectedApp}/${AppState.selectedLocale}?month_a=${AppState.selectedMonthA}&month_b=${AppState.selectedMonthB}`;
    window.open(url, "_blank");
}

// Helper formatting utilities
function formatMonthString(monthStr) {
    if (!monthStr || monthStr.length !== 6) return monthStr;
    const mm = monthStr.substring(0, 2);
    const yyyy = monthStr.substring(2);
    const months = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun", 
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ];
    const idx = parseInt(mm, 10) - 1;
    if (idx >= 0 && idx < 12) {
        return `${months[idx]} ${yyyy}`;
    }
    return monthStr;
}
window.formatMonthString = formatMonthString; // export to global namespace
