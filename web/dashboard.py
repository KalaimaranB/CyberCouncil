"""
Web Dashboard

Full web interface for CyberCouncil with real-time updates.
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import os
import logging
from functools import wraps

# Suppress Flask logs
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

_app = None
_socketio = None
_council_context = None


def create_dashboard_app(council_context=None):
    """Create Flask app with dashboard routes."""
    global _council_context
    _council_context = council_context
    
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    app.config['SECRET_KEY'] = 'council-secret-key'
    
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    # Token auth decorator
    def require_token(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            from utils.config_manager import get_config
            config = get_config()
            required_token = config.get_api_token()
            
            if required_token:
                token = request.headers.get('X-API-Token') or request.args.get('token')
                if token != required_token:
                    return jsonify({'error': 'Unauthorized'}), 401
            return f(*args, **kwargs)
        return decorated
    
    # Dashboard routes
    @app.route('/')
    def dashboard():
        return render_template('dashboard.html')
    
    @app.route('/api/status')
    def api_status():
        project = _council_context.current_project if _council_context else None
        return jsonify({
            'status': 'online',
            'project': project,
            'version': '1.0.0'
        })
    
    @app.route('/api/graph')
    def api_graph():
        if _council_context and _council_context.attack_graph:
            return jsonify(_council_context.attack_graph.to_cytoscape_format())
        return jsonify({'elements': [], 'stats': {}})
    
    @app.route('/api/logs')
    def api_logs():
        logs = []
        if _council_context and _council_context.logger:
            logs = _council_context.logger.pending_logs
        return jsonify({'logs': logs})
    
    @app.route('/api/send', methods=['POST'])
    @require_token
    def api_send():
        data = request.get_json()
        message = data.get('message', '')
        # Queue for processing
        return jsonify({'status': 'queued', 'message': message})
    
    @app.route('/api/crack', methods=['POST'])
    @require_token
    def api_crack():
        data = request.get_json()
        hash_str = data.get('hash')
        wordlist = data.get('wordlist')
        
        if not hash_str:
            return jsonify({'error': 'Missing hash'}), 400
        
        from utils.hash_cracker import HashCracker
        project = _council_context.current_project if _council_context else None
        cracker = HashCracker(project)
        result = cracker.crack(hash_str, wordlist)
        
        return jsonify(result)
    
    # WebSocket events
    @socketio.on('connect')
    def handle_connect():
        emit('status', {'connected': True})
    
    @socketio.on('command')
    def handle_command(data):
        command = data.get('command', '')
        # Process and emit response
        emit('response', {'command': command, 'result': 'Processed'})
    
    return app, socketio


def broadcast_update(event: str, data: dict):
    """Broadcast update to all connected clients."""
    if _socketio:
        _socketio.emit(event, data)
