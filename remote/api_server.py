"""
Remote API Server

Flask API server for remote access from Kali VM.
Allows sending commands, receiving responses, and importing tool output.

Start: /server start
Stop:  /server stop
"""

from flask import Flask, request, jsonify
import threading
import time
import queue
from datetime import datetime

# Message queues for bidirectional communication
_incoming_queue = queue.Queue()
_outgoing_queue = queue.Queue()
_server_thread = None
_server_running = False
_app = None
_council_context = None


def create_app():
    """Create Flask application."""
    app = Flask(__name__)
    app.config['JSON_SORT_KEYS'] = False
    
    @app.route('/api/status', methods=['GET'])
    def status():
        """Get server and project status."""
        project = _council_context.current_project if _council_context else None
        return jsonify({
            'status': 'online',
            'project': project,
            'timestamp': datetime.now().isoformat()
        })
    
    @app.route('/api/send', methods=['POST'])
    def send_message():
        """
        Send a message/command to the Council.
        
        Body: {"message": "Found DC at 10.10.10.5"}
        """
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Missing message'}), 400
        
        message = data['message']
        
        # Put message in queue for processing
        _incoming_queue.put({
            'type': 'message',
            'content': message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Wait for response (with timeout)
        try:
            response = _outgoing_queue.get(timeout=60)
            return jsonify({
                'status': 'processed',
                'response': response
            })
        except queue.Empty:
            return jsonify({
                'status': 'timeout',
                'message': 'No response within 60 seconds'
            })
    
    @app.route('/api/import', methods=['POST'])
    def import_tool_output():
        """
        Import tool output (nmap, rustscan, etc.).
        
        Body: {"tool": "nmap", "output": "Nmap scan report..."}
        """
        data = request.get_json()
        if not data or 'output' not in data:
            return jsonify({'error': 'Missing output'}), 400
        
        output = data['output']
        
        # Put in queue for processing
        _incoming_queue.put({
            'type': 'tool_output',
            'content': output,
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify({
            'status': 'queued',
            'message': 'Tool output queued for processing'
        })
    
    @app.route('/api/crack', methods=['POST'])
    def crack_hash():
        """
        Queue a hash for cracking.
        
        Body: {"hash": "31d6cfe0...", "wordlist": "/path/to/wordlist.txt"}
        """
        data = request.get_json()
        if not data or 'hash' not in data:
            return jsonify({'error': 'Missing hash'}), 400
        
        _incoming_queue.put({
            'type': 'crack',
            'hash': data['hash'],
            'wordlist': data.get('wordlist'),
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify({
            'status': 'queued',
            'message': 'Hash queued for cracking'
        })
    
    @app.route('/api/graph', methods=['GET'])
    def get_graph():
        """Get attack graph data."""
        if _council_context and _council_context.attack_graph:
            return jsonify(_council_context.attack_graph.to_cytoscape_format())
        return jsonify({'error': 'No graph available'}), 404
    
    return app


def start_server(context, port: int = 5051) -> bool:
    """
    Start the API server.
    
    Args:
        context: CyberCouncil instance
        port: Port to listen on
    """
    global _server_thread, _server_running, _app, _council_context
    
    if _server_running:
        print(f"⚠️  Server already running on port {port}")
        return False
    
    _council_context = context
    _app = create_app()
    
    def run_server():
        global _server_running
        _server_running = True
        try:
            # Suppress Flask logs
            import logging
            log = logging.getLogger('werkzeug')
            log.setLevel(logging.ERROR)
            
            _app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
        finally:
            _server_running = False
    
    _server_thread = threading.Thread(target=run_server, daemon=True)
    _server_thread.start()
    
    # Wait for server to start
    time.sleep(0.5)
    
    return True


def stop_server():
    """Stop the API server."""
    global _server_running
    _server_running = False
    # Note: Flask doesn't have a clean shutdown, server will stop when process exits


def is_running() -> bool:
    """Check if server is running."""
    return _server_running


def get_next_message(timeout: float = 0.1):
    """Get next incoming message from queue."""
    try:
        return _incoming_queue.get(timeout=timeout)
    except queue.Empty:
        return None


def send_response(response: str):
    """Send response back to remote client."""
    _outgoing_queue.put(response)


def get_local_ip():
    """Get local IP address for display."""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"
