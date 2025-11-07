// UPDATED BY CLAUDE: Shared JavaScript utilities for all frontend pages

// UPDATED BY CLAUDE: Global API base URL
const API_BASE = "http://localhost:8000";

// UPDATED BY CLAUDE: Safe fetch helper with error handling
async function safeFetch(url, options = {}) {
    const res = await fetch(API_BASE + url, options);
    if (!res.ok) {
        const text = await res.text();
        throw new Error(`HTTP ${res.status}: ${text}`);
    }
    return await res.json();
}

// UPDATED BY CLAUDE: Fetch and display logs
async function fetchLogs() {
    const logsDiv = document.getElementById('logs');
    if (!logsDiv) return;

    logsDiv.textContent = 'Loading logs...';

    try {
        const data = await safeFetch('/logs/recent?n=20', { method: 'GET' });
        const logs = data.items || [];

        if (logs.length === 0) {
            logsDiv.textContent = 'No logs yet';
            return;
        }

        logsDiv.textContent = logs.reverse().map(log =>
            `${log.timestamp || 'N/A'} [${log.endpoint || 'unknown'}] ${log.event_type || 'info'}: ${log.message || 'N/A'}`
        ).join('\n');
    } catch (err) {
        logsDiv.textContent = `Error loading logs: ${err.message}`;
    }
}

// UPDATED BY CLAUDE: Clear logs
async function clearLogs() {
    try {
        await safeFetch('/logs/clear', { method: 'POST' });
        await fetchLogs();
    } catch (err) {
        alert(`Error clearing logs: ${err.message}`);
    }
}

// UPDATED BY CLAUDE: Display response in output element
function displayResponse(elementId, data) {
    const outputElem = document.getElementById(elementId);
    if (!outputElem) return;

    outputElem.textContent = JSON.stringify(data, null, 2);
    outputElem.style.display = 'block';
}

// UPDATED BY CLAUDE: Theme toggle functionality
function toggleTheme() {
    const currentTheme = localStorage.getItem('theme') || 'dark';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

    if (newTheme === 'light') {
        document.body.classList.add('light-mode');
    } else {
        document.body.classList.remove('light-mode');
    }

    localStorage.setItem('theme', newTheme);
    updateThemeButton();
}

// UPDATED BY CLAUDE: Update theme button text
function updateThemeButton() {
    const themeBtn = document.getElementById('theme-toggle');
    if (!themeBtn) return;

    const currentTheme = localStorage.getItem('theme') || 'dark';
    themeBtn.textContent = currentTheme === 'dark' ? '☀️ Light Mode' : '🌙 Dark Mode';
}

// UPDATED BY CLAUDE: Initialize theme on page load
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'dark';

    if (savedTheme === 'light') {
        document.body.classList.add('light-mode');
    }

    updateThemeButton();
}

// UPDATED BY CLAUDE: Load logs and initialize theme on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        initializeTheme();
        fetchLogs();
    });
} else {
    initializeTheme();
    fetchLogs();
}
