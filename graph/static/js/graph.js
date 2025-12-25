/**
 * CyberCouncil Attack Graph Visualization
 * 
 * Interactive graph visualization using Cytoscape.js
 * Features: pan/zoom, filtering, path finding, export
 */

// Global state
let cy = null;
let graphData = null;

// Node type colors (matching backend)
const NODE_COLORS = {
    'IP': '#3B82F6',
    'SERVICE': '#22C55E',
    'PORT': '#EAB308',
    'VULNERABILITY': '#EF4444',
    'CREDENTIAL': '#A855F7',
    'USERNAME': '#06B6D4',
    'DOMAIN': '#F8FAFC',
    'ACCESS': '#10B981',
    'UNKNOWN': '#6B7280'
};

// Cytoscape style configuration
const CYTOSCAPE_STYLE = [
    // Node base style
    {
        selector: 'node',
        style: {
            'label': 'data(label)',
            'text-valign': 'bottom',
            'text-halign': 'center',
            'text-margin-y': 8,
            'font-size': '11px',
            'font-family': '"SF Mono", Monaco, monospace',
            'color': '#E5E7EB',
            'text-outline-color': '#111827',
            'text-outline-width': 2,
            'background-color': 'data(color)',
            'width': 40,
            'height': 40,
            'border-width': 2,
            'border-color': '#374151',
            'transition-property': 'background-color, border-color, width, height',
            'transition-duration': '0.2s'
        }
    },
    // Node type specific styles
    {
        selector: 'node.ip',
        style: {
            'shape': 'ellipse',
            'width': 50,
            'height': 50
        }
    },
    {
        selector: 'node.vulnerability',
        style: {
            'shape': 'diamond',
            'width': 45,
            'height': 45
        }
    },
    {
        selector: 'node.service',
        style: {
            'shape': 'round-rectangle'
        }
    },
    {
        selector: 'node.port',
        style: {
            'shape': 'round-rectangle',
            'width': 35,
            'height': 35
        }
    },
    {
        selector: 'node.credential, node.username',
        style: {
            'shape': 'tag'
        }
    },
    {
        selector: 'node.domain',
        style: {
            'shape': 'hexagon',
            'width': 55,
            'height': 55
        }
    },
    {
        selector: 'node.access',
        style: {
            'shape': 'star',
            'width': 45,
            'height': 45
        }
    },
    // Edge styles
    {
        selector: 'edge',
        style: {
            'width': 2,
            'line-color': '#4B5563',
            'target-arrow-color': '#4B5563',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'label': 'data(label)',
            'font-size': '9px',
            'font-family': '"SF Mono", Monaco, monospace',
            'color': '#9CA3AF',
            'text-rotation': 'autorotate',
            'text-margin-y': -8,
            'text-outline-color': '#111827',
            'text-outline-width': 1
        }
    },
    // Interactive states
    {
        selector: 'node:selected',
        style: {
            'border-width': 4,
            'border-color': '#F59E0B',
            'background-color': '#F59E0B'
        }
    },
    {
        selector: 'node.highlighted',
        style: {
            'border-width': 4,
            'border-color': '#10B981',
            'z-index': 999
        }
    },
    {
        selector: 'node.path-node',
        style: {
            'border-width': 4,
            'border-color': '#EC4899',
            'background-opacity': 1,
            'z-index': 1000
        }
    },
    {
        selector: 'edge.path-edge',
        style: {
            'line-color': '#EC4899',
            'target-arrow-color': '#EC4899',
            'width': 4,
            'z-index': 1000
        }
    },
    {
        selector: 'node.dimmed',
        style: {
            'opacity': 0.3
        }
    },
    {
        selector: 'edge.dimmed',
        style: {
            'opacity': 0.2
        }
    },
    {
        selector: 'node.hidden',
        style: {
            'display': 'none'
        }
    }
];

// Initialize the graph
async function initGraph() {
    try {
        const response = await fetch('/api/graph');
        graphData = await response.json();

        // Show/hide empty state
        const emptyState = document.getElementById('emptyState');
        const cyElement = document.getElementById('cy');

        if (!graphData.elements || graphData.elements.length === 0) {
            emptyState.style.display = 'flex';
            cyElement.style.opacity = '0.3';
        } else {
            emptyState.style.display = 'none';
            cyElement.style.opacity = '1';
        }

        // Initialize Cytoscape
        cy = cytoscape({
            container: document.getElementById('cy'),
            elements: graphData.elements,
            style: CYTOSCAPE_STYLE,
            layout: {
                name: 'cose',
                animate: true,
                animationDuration: 500,
                nodeDimensionsIncludeLabels: true,
                padding: 50
            },
            minZoom: 0.1,
            maxZoom: 3,
            wheelSensitivity: 0.2
        });

        // Update statistics
        updateStats(graphData.stats);

        // Populate path finder dropdowns
        populatePathSelectors();

        // Set up event listeners
        setupEventListeners();

    } catch (error) {
        console.error('Failed to load graph:', error);
        document.getElementById('connectionStatus').className = 'status-indicator status-disconnected';
        document.getElementById('connectionStatus').textContent = '● Disconnected';
    }
}

// Update statistics display
function updateStats(stats) {
    document.getElementById('statNodes').textContent = stats.total_nodes || 0;
    document.getElementById('statEdges').textContent = stats.total_edges || 0;
}

// Populate path finder dropdowns with node options
function populatePathSelectors() {
    const sourceSelect = document.getElementById('pathSource');
    const targetSelect = document.getElementById('pathTarget');

    // Clear existing options
    sourceSelect.innerHTML = '<option value="">Select start node...</option>';
    targetSelect.innerHTML = '<option value="">Select end node...</option>';

    // Get all nodes sorted by type priority
    const nodes = cy.nodes().sort((a, b) => {
        const typePriority = ['IP', 'VULNERABILITY', 'SERVICE', 'CREDENTIAL', 'PORT'];
        const aType = a.data('type');
        const bType = b.data('type');
        return typePriority.indexOf(aType) - typePriority.indexOf(bType);
    });

    nodes.forEach(node => {
        const id = node.id();
        const type = node.data('type');
        const option1 = document.createElement('option');
        option1.value = id;
        option1.textContent = `[${type}] ${id}`;
        sourceSelect.appendChild(option1);

        const option2 = document.createElement('option');
        option2.value = id;
        option2.textContent = `[${type}] ${id}`;
        targetSelect.appendChild(option2);
    });
}

// Set up all event listeners
function setupEventListeners() {
    // Node click - show details
    cy.on('tap', 'node', function (evt) {
        const node = evt.target;
        showNodeDetails(node);
    });

    // Background click - clear selection
    cy.on('tap', function (evt) {
        if (evt.target === cy) {
            clearNodeDetails();
            cy.nodes().removeClass('highlighted');
        }
    });

    // Node hover effects
    cy.on('mouseover', 'node', function (evt) {
        const node = evt.target;
        node.addClass('highlighted');
    });

    cy.on('mouseout', 'node', function (evt) {
        const node = evt.target;
        if (!node.selected()) {
            node.removeClass('highlighted');
        }
    });

    // Layout selector
    document.getElementById('layoutSelect').addEventListener('change', function () {
        changeLayout(this.value);
    });

    // Refresh button
    document.getElementById('refreshBtn').addEventListener('click', refreshGraph);

    // Fit button
    document.getElementById('fitBtn').addEventListener('click', () => {
        cy.fit(50);
    });

    // Export buttons
    document.getElementById('exportPngBtn').addEventListener('click', exportPng);
    document.getElementById('exportJsonBtn').addEventListener('click', exportJson);

    // Search input
    document.getElementById('searchInput').addEventListener('input', function () {
        searchNodes(this.value);
    });

    // Filter checkboxes
    document.querySelectorAll('#filterPanel input[type="checkbox"]').forEach(checkbox => {
        checkbox.addEventListener('change', applyFilters);
    });

    // Path finder buttons
    document.getElementById('findPathBtn').addEventListener('click', findPath);
    document.getElementById('clearPathBtn').addEventListener('click', clearPath);
}

// Show node details in the side panel
function showNodeDetails(node) {
    const data = node.data();
    const detailsDiv = document.getElementById('nodeDetails');
    const neighborsPanel = document.getElementById('neighborsPanel');
    const neighborsList = document.getElementById('neighborsList');

    // Build details HTML
    let html = `
        <div class="detail-header">
            <span class="detail-type" style="color: ${data.color}">${data.type}</span>
        </div>
        <div class="detail-id">${node.id()}</div>
        <div class="detail-attributes">
    `;

    // Add all attributes
    Object.entries(data).forEach(([key, value]) => {
        if (!['id', 'label', 'color', 'type'].includes(key)) {
            html += `
                <div class="detail-attr">
                    <span class="attr-key">${key}:</span>
                    <span class="attr-value">${value}</span>
                </div>
            `;
        }
    });

    html += `
        </div>
        <div class="detail-actions">
            <button class="btn btn-small" onclick="copyToClipboard('${node.id()}')">📋 Copy ID</button>
            <button class="btn btn-small" onclick="focusNeighborhood('${node.id()}')">🔍 Focus</button>
        </div>
    `;

    detailsDiv.innerHTML = html;

    // Show neighbors
    const neighbors = node.neighborhood().nodes();
    if (neighbors.length > 0) {
        neighborsPanel.style.display = 'block';
        let neighborsHtml = '';
        neighbors.forEach(neighbor => {
            const nData = neighbor.data();
            neighborsHtml += `
                <div class="neighbor-item" onclick="cy.$('#${neighbor.id()}').trigger('tap')">
                    <span class="neighbor-icon" style="color: ${nData.color}">●</span>
                    <span class="neighbor-id">${neighbor.id()}</span>
                    <span class="neighbor-type">${nData.type}</span>
                </div>
            `;
        });
        neighborsList.innerHTML = neighborsHtml;
    } else {
        neighborsPanel.style.display = 'none';
    }
}

// Clear node details panel
function clearNodeDetails() {
    document.getElementById('nodeDetails').innerHTML = '<p class="hint">Click a node to see details</p>';
    document.getElementById('neighborsPanel').style.display = 'none';
}

// Change graph layout
function changeLayout(layoutName) {
    cy.layout({
        name: layoutName,
        animate: true,
        animationDuration: 500,
        nodeDimensionsIncludeLabels: true,
        padding: 50,
        // Hierarchical specific
        spacingFactor: layoutName === 'breadthfirst' ? 1.5 : 1,
        // Concentric specific  
        concentric: layoutName === 'concentric' ? node => {
            const typePriority = { 'IP': 4, 'VULNERABILITY': 3, 'SERVICE': 2, 'PORT': 1 };
            return typePriority[node.data('type')] || 0;
        } : undefined
    }).run();
}

// Refresh graph data from server
async function refreshGraph() {
    try {
        await fetch('/api/refresh');
        await initGraph();
        console.log('Graph refreshed');
    } catch (error) {
        console.error('Failed to refresh graph:', error);
    }
}

// Export graph as PNG
function exportPng() {
    const png = cy.png({
        output: 'blob',
        bg: '#111827',
        full: true,
        scale: 2
    });

    const link = document.createElement('a');
    link.href = URL.createObjectURL(png);
    link.download = 'attack_graph.png';
    link.click();
}

// Export graph as JSON
function exportJson() {
    const data = JSON.stringify(graphData, null, 2);
    const blob = new Blob([data], { type: 'application/json' });

    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'attack_graph.json';
    link.click();
}

// Search nodes by text
function searchNodes(query) {
    if (!query) {
        cy.nodes().removeClass('dimmed highlighted');
        cy.edges().removeClass('dimmed');
        return;
    }

    query = query.toLowerCase();

    cy.nodes().forEach(node => {
        const id = node.id().toLowerCase();
        const type = (node.data('type') || '').toLowerCase();
        const matches = id.includes(query) || type.includes(query);

        if (matches) {
            node.removeClass('dimmed').addClass('highlighted');
        } else {
            node.removeClass('highlighted').addClass('dimmed');
        }
    });

    cy.edges().addClass('dimmed');
}

// Apply type filters
function applyFilters() {
    const activeTypes = [];
    document.querySelectorAll('#filterPanel input[type="checkbox"]:checked').forEach(cb => {
        activeTypes.push(cb.dataset.type.toUpperCase());
    });

    cy.nodes().forEach(node => {
        const type = node.data('type');
        if (activeTypes.includes(type)) {
            node.removeClass('hidden');
        } else {
            node.addClass('hidden');
        }
    });
}

// Find shortest path between two nodes
function findPath() {
    const sourceId = document.getElementById('pathSource').value;
    const targetId = document.getElementById('pathTarget').value;

    if (!sourceId || !targetId) {
        alert('Please select both source and target nodes');
        return;
    }

    // Clear previous path
    clearPath();

    // Use Dijkstra's algorithm
    const dijkstra = cy.elements().dijkstra({
        root: '#' + CSS.escape(sourceId),
        directed: true
    });

    const targetNode = cy.$('#' + CSS.escape(targetId));
    const pathToTarget = dijkstra.pathTo(targetNode);

    if (pathToTarget.length === 0) {
        alert('No path found between selected nodes');
        return;
    }

    // Highlight path
    pathToTarget.forEach(ele => {
        if (ele.isNode()) {
            ele.addClass('path-node');
        } else {
            ele.addClass('path-edge');
        }
    });

    // Dim other elements
    cy.elements().not(pathToTarget).addClass('dimmed');

    // Fit to path
    cy.fit(pathToTarget, 100);
}

// Clear path highlighting
function clearPath() {
    cy.elements().removeClass('path-node path-edge dimmed');
}

// Focus on a node's neighborhood
function focusNeighborhood(nodeId) {
    const node = cy.$('#' + CSS.escape(nodeId));
    const neighborhood = node.neighborhood().add(node);

    cy.elements().addClass('dimmed');
    neighborhood.removeClass('dimmed');

    cy.fit(neighborhood, 50);
}

// Copy text to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        console.log('Copied to clipboard:', text);
    }).catch(err => {
        console.error('Failed to copy:', err);
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initGraph);
