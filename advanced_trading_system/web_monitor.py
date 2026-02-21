#!/usr/bin/env python3
"""
Web-based Monitoring Dashboard for Autonomous AI
Real-time web interface for monitoring and control
"""
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
import os
from pathlib import Path
from datetime import datetime
import threading
import time

app = Flask(__name__)
CORS(app)

# Global status
current_status = {
    'is_running': False,
    'autonomy_level': 'unknown',
    'decisions_made': 0,
    'trades_executed': 0,
    'wins': 0,
    'losses': 0,
    'total_pnl': 0.0,
    'health_status': 'unknown',
    'last_update': datetime.now().isoformat()
}


def update_status_loop():
    """Background thread to update status"""
    global current_status
    
    while True:
        try:
            # Read status from file
            status_file = 'data/autonomous_status.json'
            if Path(status_file).exists():
                with open(status_file, 'r') as f:
                    data = json.load(f)
                    current_status.update(data)
                    current_status['last_update'] = datetime.now().isoformat()
        except Exception as e:
            print(f"Error updating status: {e}")
        
        time.sleep(5)  # Update every 5 seconds


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')


@app.route('/api/status')
def get_status():
    """Get current status"""
    return jsonify(current_status)


@app.route('/api/metrics')
def get_metrics():
    """Get detailed metrics"""
    try:
        # Read metrics from file
        metrics_file = 'data/autonomous_metrics.json'
        if Path(metrics_file).exists():
            with open(metrics_file, 'r') as f:
                metrics = json.load(f)
                return jsonify(metrics)
    except:
        pass
    
    return jsonify({
        'decisions': [],
        'performance': [],
        'health': []
    })


@app.route('/api/logs')
def get_logs():
    """Get recent logs"""
    try:
        log_files = sorted(Path('logs').glob('autonomous_ai_*.log'), reverse=True)
        if log_files:
            with open(log_files[0], 'r') as f:
                lines = f.readlines()[-50:]  # Last 50 lines
                return jsonify({'logs': [line.strip() for line in lines]})
    except:
        pass
    
    return jsonify({'logs': []})


@app.route('/api/control/<action>', methods=['POST'])
def control_action(action):
    """Control autonomous AI"""
    if action == 'pause':
        # Implement pause logic
        return jsonify({'success': True, 'message': 'System paused'})
    elif action == 'resume':
        # Implement resume logic
        return jsonify({'success': True, 'message': 'System resumed'})
    elif action == 'stop':
        # Implement stop logic
        return jsonify({'success': True, 'message': 'System stopping...'})
    
    return jsonify({'success': False, 'message': 'Unknown action'})


def create_html_template():
    """Create HTML template for dashboard"""
    os.makedirs('templates', exist_ok=True)
    
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Autonomous AI Monitor</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0a0e27;
            color: #e0e0e0;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
        .header h1 { color: white; font-size: 2.5em; margin-bottom: 10px; }
        .header .timestamp { color: #f0f0f0; font-size: 1.1em; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 20px; }
        .card {
            background: #1a1f3a;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        .card h2 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.3em;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        .metric {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #2a2f4a;
        }
        .metric:last-child { border-bottom: none; }
        .metric-label { color: #a0a0a0; }
        .metric-value { font-weight: bold; font-size: 1.1em; }
        .status-running { color: #4ade80; }
        .status-stopped { color: #f87171; }
        .status-warning { color: #fbbf24; }
        .health-healthy { color: #4ade80; }
        .health-warning { color: #fbbf24; }
        .health-critical { color: #f87171; }
        .logs {
            background: #0f1419;
            padding: 15px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            max-height: 400px;
            overflow-y: auto;
        }
        .log-line { padding: 5px 0; border-bottom: 1px solid #1a1f3a; }
        .controls {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
            font-weight: bold;
            transition: all 0.3s;
        }
        .btn-primary { background: #667eea; color: white; }
        .btn-primary:hover { background: #5568d3; }
        .btn-danger { background: #f87171; color: white; }
        .btn-danger:hover { background: #dc2626; }
        .btn-warning { background: #fbbf24; color: #0a0e27; }
        .btn-warning:hover { background: #f59e0b; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Autonomous AI Trading Monitor</h1>
            <div class="timestamp" id="timestamp"></div>
        </div>
        
        <div class="grid">
            <div class="card">
                <h2>System Status</h2>
                <div class="metric">
                    <span class="metric-label">Status:</span>
                    <span class="metric-value" id="status">Loading...</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Autonomy Level:</span>
                    <span class="metric-value" id="autonomy">-</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Learning:</span>
                    <span class="metric-value" id="learning">-</span>
                </div>
            </div>
            
            <div class="card">
                <h2>Performance</h2>
                <div class="metric">
                    <span class="metric-label">Decisions Made:</span>
                    <span class="metric-value" id="decisions">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Trades Executed:</span>
                    <span class="metric-value" id="trades">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Win Rate:</span>
                    <span class="metric-value" id="winrate">0%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Total P&L:</span>
                    <span class="metric-value" id="pnl">$0.00</span>
                </div>
            </div>
            
            <div class="card">
                <h2>Health Status</h2>
                <div class="metric">
                    <span class="metric-label">Health:</span>
                    <span class="metric-value" id="health">Unknown</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Issues:</span>
                    <span class="metric-value" id="issues">0</span>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>Recent Activity</h2>
            <div class="logs" id="logs">
                <div class="log-line">Waiting for data...</div>
            </div>
        </div>
        
        <div class="controls">
            <button class="btn btn-warning" onclick="pauseSystem()">⏸️ Pause</button>
            <button class="btn btn-primary" onclick="resumeSystem()">▶️ Resume</button>
            <button class="btn btn-danger" onclick="stopSystem()">⏹️ Stop</button>
        </div>
    </div>
    
    <script>
        function updateDashboard() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    // Update timestamp
                    document.getElementById('timestamp').textContent = new Date().toLocaleString();
                    
                    // Update status
                    const statusEl = document.getElementById('status');
                    if (data.is_running) {
                        statusEl.textContent = '✅ RUNNING';
                        statusEl.className = 'metric-value status-running';
                    } else {
                        statusEl.textContent = '❌ STOPPED';
                        statusEl.className = 'metric-value status-stopped';
                    }
                    
                    // Update autonomy
                    document.getElementById('autonomy').textContent = (data.autonomy_level || 'unknown').toUpperCase();
                    
                    // Update learning
                    const learningEl = document.getElementById('learning');
                    if (data.is_learning) {
                        learningEl.textContent = '✅ ACTIVE';
                        learningEl.className = 'metric-value status-running';
                    } else {
                        learningEl.textContent = '❌ INACTIVE';
                        learningEl.className = 'metric-value status-stopped';
                    }
                    
                    // Update performance
                    document.getElementById('decisions').textContent = data.decisions_made || 0;
                    
                    const perf = data.current_performance || {};
                    const trades = perf.total_trades || 0;
                    const wins = perf.wins || 0;
                    const losses = perf.losses || 0;
                    const pnl = perf.total_pnl || 0;
                    
                    document.getElementById('trades').textContent = trades;
                    
                    if (trades > 0) {
                        const winRate = (wins / trades * 100).toFixed(1);
                        const winRateEl = document.getElementById('winrate');
                        winRateEl.textContent = winRate + '%';
                        winRateEl.className = 'metric-value ' + (winRate >= 50 ? 'status-running' : 'status-stopped');
                    }
                    
                    const pnlEl = document.getElementById('pnl');
                    pnlEl.textContent = '$' + pnl.toFixed(2);
                    pnlEl.className = 'metric-value ' + (pnl >= 0 ? 'status-running' : 'status-stopped');
                    
                    // Update health
                    const health = data.health_status || {};
                    const healthStatus = health.status || 'unknown';
                    const healthEl = document.getElementById('health');
                    
                    if (healthStatus === 'healthy') {
                        healthEl.textContent = '✅ HEALTHY';
                        healthEl.className = 'metric-value health-healthy';
                    } else if (healthStatus === 'warning') {
                        healthEl.textContent = '⚠️ WARNING';
                        healthEl.className = 'metric-value health-warning';
                    } else if (healthStatus === 'critical') {
                        healthEl.textContent = '🚨 CRITICAL';
                        healthEl.className = 'metric-value health-critical';
                    } else {
                        healthEl.textContent = '❓ UNKNOWN';
                        healthEl.className = 'metric-value status-warning';
                    }
                    
                    const issues = health.issues || [];
                    document.getElementById('issues').textContent = issues.length;
                })
                .catch(error => console.error('Error fetching status:', error));
            
            // Update logs
            fetch('/api/logs')
                .then(response => response.json())
                .then(data => {
                    const logsEl = document.getElementById('logs');
                    const logs = data.logs || [];
                    
                    if (logs.length > 0) {
                        logsEl.innerHTML = logs.map(log => 
                            `<div class="log-line">${log}</div>`
                        ).join('');
                    }
                })
                .catch(error => console.error('Error fetching logs:', error));
        }
        
        function pauseSystem() {
            if (confirm('Pause autonomous AI system?')) {
                fetch('/api/control/pause', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => alert(data.message))
                    .catch(error => alert('Error: ' + error));
            }
        }
        
        function resumeSystem() {
            if (confirm('Resume autonomous AI system?')) {
                fetch('/api/control/resume', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => alert(data.message))
                    .catch(error => alert('Error: ' + error));
            }
        }
        
        function stopSystem() {
            if (confirm('Stop autonomous AI system? This will end the current session.')) {
                fetch('/api/control/stop', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => alert(data.message))
                    .catch(error => alert('Error: ' + error));
            }
        }
        
        // Update every 5 seconds
        setInterval(updateDashboard, 5000);
        
        // Initial update
        updateDashboard();
    </script>
</body>
</html>
    """
    
    with open('templates/dashboard.html', 'w') as f:
        f.write(html_content)


def main():
    """Main entry point"""
    print("🌐 Starting Web-based Monitoring Dashboard...")
    
    # Create templates directory
    os.makedirs('templates', exist_ok=True)
    create_html_template()
    
    # Start status update thread
    status_thread = threading.Thread(target=update_status_loop, daemon=True)
    status_thread.start()
    
    print("\n" + "="*80)
    print("✅ Web Monitor Started")
    print("="*80)
    print("\n📊 Dashboard URL: http://localhost:5000")
    print("\n⚠️  Keep this terminal open while monitoring")
    print("   Press Ctrl+C to stop the web server")
    print("\n" + "="*80)
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=False)


if __name__ == '__main__':
    main()