"""
Graph Server Module

Lightweight Flask server for serving the interactive attack graph visualization.
Serves both the web UI and API endpoints for graph data.
"""

import os
import socket
import threading
import webbrowser
from flask import Flask, render_template, jsonify
from typing import Optional

# Graph will be injected at runtime
_current_graph = None
_server_thread = None
_server_running = False


def create_app(graph=None):
    """
    Create Flask application for graph visualization.
    
    Args:
        graph: AttackGraph instance to visualize
        
    Returns:
        Flask app configured with routes
    """
    global _current_graph
    _current_graph = graph
    
    # Set up template and static directories
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    
    # Disable Flask's default logging for cleaner terminal output
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    
    @app.route('/')
    def index():
        """Serve the main visualization page"""
        return render_template('index.html')
    
    @app.route('/api/graph')
    def get_graph():
        """Return graph data in Cytoscape.js format"""
        global _current_graph
        if _current_graph is None:
            return jsonify({
                'elements': [],
                'stats': {'total_nodes': 0, 'total_edges': 0}
            })
        return jsonify(_current_graph.to_cytoscape_format())
    
    @app.route('/api/stats')
    def get_stats():
        """Return graph statistics"""
        global _current_graph
        if _current_graph is None:
            return jsonify({'total_nodes': 0, 'total_edges': 0})
        return jsonify(_current_graph.get_statistics())
    
    @app.route('/api/refresh')
    def refresh_graph():
        """Reload graph from active_record.md"""
        global _current_graph
        if _current_graph is not None:
            from core import config
            active_record_path = f"{config.PROJECTS_DIR}/{_current_graph.project_name}/active_record.md"
            _current_graph.parse_active_record(active_record_path)
        return jsonify({'status': 'refreshed'})
    
    return app


def find_available_port(start_port: int = 5050, max_attempts: int = 10) -> int:
    """
    Find an available port starting from start_port.
    
    Args:
        start_port: Port to start searching from
        max_attempts: Maximum number of ports to try
        
    Returns:
        Available port number
    """
    for port in range(start_port, start_port + max_attempts):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('127.0.0.1', port))
            sock.close()
            return port
        except OSError:
            continue
    return start_port  # Fallback


def start_server(graph, open_browser: bool = True) -> Optional[int]:
    """
    Start the graph visualization server in a background thread.
    
    Args:
        graph: AttackGraph instance to visualize
        open_browser: Whether to automatically open browser
        
    Returns:
        Port number the server is running on, or None if failed
    """
    global _server_thread, _server_running, _current_graph
    
    if _server_running:
        print("⚠️  Graph server already running")
        return None
    
    _current_graph = graph
    port = find_available_port()
    app = create_app(graph)
    
    def run_server():
        global _server_running
        _server_running = True
        try:
            app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)
        finally:
            _server_running = False
    
    _server_thread = threading.Thread(target=run_server, daemon=True)
    _server_thread.start()
    
    url = f"http://localhost:{port}"
    
    if open_browser:
        # Small delay to ensure server is ready
        import time
        time.sleep(0.5)
        webbrowser.open(url)
    
    return port


def stop_server():
    """Stop the graph visualization server."""
    global _server_running
    _server_running = False
    # Note: Flask's development server doesn't have a clean shutdown
    # The daemon thread will be killed when the main process exits


def update_graph(graph):
    """Update the graph being served."""
    global _current_graph
    _current_graph = graph


def is_running() -> bool:
    """Check if the server is currently running."""
    global _server_running
    return _server_running
