/**
 * CyberCouncil Dashboard JavaScript
 * Handles graph visualization, real-time updates, and UI interactions
 */

// State
let cy = null;
let socket = null;
let currentView = 'graph';

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    initGraph();
    initNavigation();
    initTerminal();
    initCracker();
    loadStatus();
    loadGraph();

    // Refresh button
    document.getElementById('refresh-btn').addEventListener('click', loadGraph);
});

// Initialize Cytoscape graph
function initGraph() {
    cy = cytoscape({
        container: document.getElementById('cy'),
        style: [
            {
                selector: 'node',
                style: {
                    'background-color': 'data(color)',
                    'label': 'data(label)',
                    'color': '#e4e4e7',
                    'text-valign': 'bottom',
                    'text-margin-y': 8,
                    'font-size': 12,
                    'width': 40,
                    'height': 40,
                    'border-width': 2,
                    'border-color': '#2a2a3a',
                    'transition-property': 'background-color, width, height',
                    'transition-duration': '0.2s'
                }
            },
            {
                selector: 'node:hover',
                style: {
                    'width': 50,
                    'height': 50,
                    'border-color': '#6366f1'
                }
            },
            {
                selector: 'node:selected',
                style: {
                    'border-color': '#818cf8',
                    'border-width': 3
                }
            },
            {
                selector: 'edge',
                style: {
                    'width': 2,
                    'line-color': '#3f3f46',
                    'target-arrow-color': '#3f3f46',
                    'target-arrow-shape': 'triangle',
                    'curve-style': 'bezier',
                    'opacity': 0.7
                }
            },
            {
                selector: 'edge:hover',
                style: {
                    'opacity': 1,
                    'line-color': '#6366f1'
                }
            }
        ],
        layout: { name: 'cose', animate: true, animationDuration: 500 },
        minZoom: 0.5,
        maxZoom: 3
    });

    // Node click handler
    cy.on('tap', 'node', (event) => {
        const node = event.target;
        showNodeDetails(node.data());
    });

    // Layout selector
    document.getElementById('layout-select').addEventListener('change', (e) => {
        cy.layout({ name: e.target.value, animate: true }).run();
    });

    // Search
    document.getElementById('search-input').addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();
        cy.nodes().forEach(node => {
            const label = node.data('label').toLowerCase();
            if (query && !label.includes(query)) {
                node.style('opacity', 0.2);
            } else {
                node.style('opacity', 1);
            }
        });
    });
}

// Navigation
function initNavigation() {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const view = item.dataset.view;
            switchView(view);

            // Update active state
            document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
            item.classList.add('active');
        });
    });

    // Details panel close
    document.getElementById('close-panel').addEventListener('click', () => {
        document.getElementById('details-panel').classList.remove('open');
    });
}

function switchView(view) {
    currentView = view;
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    document.getElementById(`view-${view}`).classList.add('active');

    const titles = {
        'graph': 'Attack Graph',
        'terminal': 'Terminal',
        'logs': 'Pending Logs',
        'crack': 'Hash Cracker'
    };
    document.getElementById('view-title').textContent = titles[view] || view;
}

// Terminal
function initTerminal() {
    const input = document.getElementById('terminal-input');
    const output = document.getElementById('terminal-output');

    input.addEventListener('keypress', async (e) => {
        if (e.key === 'Enter') {
            const command = input.value.trim();
            if (!command) return;

            // Add to output
            addTerminalLine(`> ${command}`, 'command');
            input.value = '';

            // Send to server
            try {
                const response = await fetch('/api/send', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: command })
                });
                const data = await response.json();
                addTerminalLine(data.response || data.message || 'OK');
            } catch (error) {
                addTerminalLine(`Error: ${error.message}`, 'error');
            }
        }
    });
}

function addTerminalLine(text, type = '') {
    const output = document.getElementById('terminal-output');
    const line = document.createElement('div');
    line.className = `line ${type}`;
    line.textContent = text;
    output.appendChild(line);
    output.scrollTop = output.scrollHeight;
}

// Hash Cracker
function initCracker() {
    document.getElementById('crack-btn').addEventListener('click', async () => {
        const hash = document.getElementById('crack-hash').value.trim();
        const wordlist = document.getElementById('crack-wordlist').value.trim();
        const result = document.getElementById('crack-result');

        if (!hash) {
            showToast('Please enter a hash', 'error');
            return;
        }

        // Show loading
        const btn = document.getElementById('crack-btn');
        btn.disabled = true;
        btn.innerHTML = '<span>⏳</span> Cracking...';

        try {
            const response = await fetch('/api/crack', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ hash, wordlist: wordlist || null })
            });
            const data = await response.json();

            if (data.status === 'cracked') {
                result.className = 'crack-result success';
                result.innerHTML = `
                    <h3>🎉 Cracked!</h3>
                    <p><strong>Password:</strong> ${data.password}</p>
                `;
            } else {
                result.className = 'crack-result error';
                result.innerHTML = `
                    <h3>❌ ${data.status}</h3>
                    <p>${data.message || 'Could not crack hash'}</p>
                `;
            }
        } catch (error) {
            result.className = 'crack-result error';
            result.innerHTML = `<p>Error: ${error.message}</p>`;
        } finally {
            btn.disabled = false;
            btn.innerHTML = '<span>⚡</span> Crack Hash';
        }
    });
}

// API Calls
async function loadStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        document.getElementById('project-name').textContent = data.project || 'No Project';
    } catch (error) {
        console.error('Failed to load status:', error);
    }
}

async function loadGraph() {
    try {
        const response = await fetch('/api/graph');
        const data = await response.json();

        if (data.elements) {
            cy.elements().remove();
            cy.add(data.elements);
            cy.layout({ name: 'cose', animate: true }).run();

            // Update stats
            const stats = data.stats || {};
            document.getElementById('stat-nodes').textContent = stats.total_nodes || cy.nodes().length;
            document.getElementById('stat-edges').textContent = stats.total_edges || cy.edges().length;
        }
    } catch (error) {
        console.error('Failed to load graph:', error);
    }
}

async function loadLogs() {
    try {
        const response = await fetch('/api/logs');
        const data = await response.json();
        const container = document.getElementById('logs-container');

        if (data.logs && data.logs.length > 0) {
            container.innerHTML = data.logs.map(log => `
                <div class="log-item">
                    <span class="log-type">${log.type || 'LOG'}</span>
                    <span class="log-content">${log.content || log}</span>
                </div>
            `).join('');
        } else {
            container.innerHTML = `
                <div class="empty-state">
                    <span class="empty-icon">📋</span>
                    <p>No pending logs</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Failed to load logs:', error);
    }
}

// Node Details Panel
function showNodeDetails(data) {
    const panel = document.getElementById('details-panel');
    const content = document.getElementById('panel-content');

    content.innerHTML = `
        <div class="detail-row">
            <label>ID</label>
            <p>${data.id}</p>
        </div>
        <div class="detail-row">
            <label>Type</label>
            <p>${data.type || 'Unknown'}</p>
        </div>
        <div class="detail-row">
            <label>Label</label>
            <p>${data.label}</p>
        </div>
        ${data.context ? `
        <div class="detail-row">
            <label>Context</label>
            <p>${data.context}</p>
        </div>
        ` : ''}
    `;

    panel.classList.add('open');
}

// Toast notifications
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    const icons = { info: 'ℹ️', success: '✅', error: '❌', warning: '⚠️' };
    toast.innerHTML = `<span>${icons[type] || 'ℹ️'}</span><span>${message}</span>`;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// WebSocket (if available)
function initWebSocket() {
    if (typeof io !== 'undefined') {
        socket = io();

        socket.on('connect', () => {
            console.log('WebSocket connected');
        });

        socket.on('graph_update', (data) => {
            loadGraph();
            showToast('Graph updated', 'info');
        });

        socket.on('response', (data) => {
            addTerminalLine(data.result);
        });
    }
}
