"""MJPEG streaming via Flask for browser viewing without X11."""
import logging
import cv2
from flask import Flask, Response, render_template_string, jsonify, request
import threading
import json

log = logging.getLogger('Streamer')

class MJPEGStreamer:
    def __init__(self, camera_worker, sensors=None, motor=None, host='0.0.0.0', port=5000):
        self.camera_worker = camera_worker
        self.sensors = sensors
        self.motor = motor
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        self._setup_routes()
        self._stopped = False

    def _setup_routes(self):
        @self.app.route('/')
        def index():
            return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>RaspiTank Control Center</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: white;
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        h1 {
            text-align: center;
            color: #4CAF50;
            margin-bottom: 20px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }
        .main-grid {
            display: grid;
            grid-template-columns: 1fr 350px;
            gap: 20px;
            margin-bottom: 20px;
        }
        @media (max-width: 1024px) {
            .main-grid {
                grid-template-columns: 1fr;
            }
        }
        .video-container {
            background: #2a2a3e;
            border-radius: 12px;
            padding: 15px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.3);
        }
        .video-container img {
            width: 100%;
            border-radius: 8px;
            display: block;
        }
        .sidebar {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        .panel {
            background: #2a2a3e;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.3);
        }
        .panel h2 {
            color: #4CAF50;
            margin-bottom: 15px;
            font-size: 1.4em;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 8px;
        }
        .sensor-grid {
            display: grid;
            gap: 12px;
        }
        .sensor-item {
            background: #1a1a2e;
            padding: 12px;
            border-radius: 8px;
            border-left: 4px solid #4CAF50;
        }
        .sensor-label {
            color: #888;
            font-size: 0.85em;
            margin-bottom: 4px;
        }
        .sensor-value {
            font-size: 1.5em;
            font-weight: bold;
            color: #4CAF50;
        }
        .sensor-unit {
            font-size: 0.9em;
            color: #aaa;
            margin-left: 4px;
        }
        .warning {
            border-left-color: #ff9800 !important;
        }
        .warning .sensor-value {
            color: #ff9800;
        }
        .danger {
            border-left-color: #f44336 !important;
        }
        .danger .sensor-value {
            color: #f44336;
        }
        .controls {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 15px;
        }
        .control-pad {
            display: grid;
            grid-template-columns: repeat(3, 80px);
            grid-template-rows: repeat(3, 80px);
            gap: 8px;
            margin: 10px 0;
        }
        .control-btn {
            background: linear-gradient(145deg, #4CAF50, #388E3C);
            border: none;
            border-radius: 12px;
            color: white;
            font-size: 1.5em;
            cursor: pointer;
            transition: all 0.1s;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            user-select: none;
        }
        .control-btn:hover {
            background: linear-gradient(145deg, #66BB6A, #4CAF50);
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.4);
        }
        .control-btn:active {
            transform: translateY(0);
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        .control-btn:disabled {
            background: #555;
            cursor: not-allowed;
            opacity: 0.5;
        }
        .btn-up { grid-column: 2; grid-row: 1; }
        .btn-left { grid-column: 1; grid-row: 2; }
        .btn-stop { 
            grid-column: 2; 
            grid-row: 2;
            background: linear-gradient(145deg, #f44336, #c62828);
            font-size: 1.2em;
        }
        .btn-stop:hover {
            background: linear-gradient(145deg, #e57373, #f44336);
        }
        .btn-right { grid-column: 3; grid-row: 2; }
        .btn-down { grid-column: 2; grid-row: 3; }
        .status-indicator {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 10px;
            background: #1a1a2e;
            border-radius: 8px;
            margin-bottom: 10px;
        }
        .status-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #4CAF50;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .status-offline {
            background: #f44336;
        }
        .keyboard-hint {
            text-align: center;
            color: #888;
            font-size: 0.85em;
            margin-top: 10px;
        }
        .info-bar {
            background: #2a2a3e;
            border-radius: 12px;
            padding: 15px;
            text-align: center;
            box-shadow: 0 8px 16px rgba(0,0,0,0.3);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 RaspiTank Control Center</h1>
        
        <div class="main-grid">
            <div class="video-container">
                <img src="{{ url_for('video_feed') }}" alt="Video Stream">
            </div>
            
            <div class="sidebar">
                <div class="panel">
                    <h2>📡 Sensors</h2>
                    <div class="status-indicator">
                        <div class="status-dot" id="status-dot"></div>
                        <span id="status-text">Connecting...</span>
                    </div>
                    <div class="sensor-grid" id="sensor-data">
                        <div class="sensor-item">
                            <div class="sensor-label">Front Distance</div>
                            <div class="sensor-value" id="front-dist">--<span class="sensor-unit">cm</span></div>
                        </div>
                        <div class="sensor-item">
                            <div class="sensor-label">Left Distance</div>
                            <div class="sensor-value" id="left-dist">--<span class="sensor-unit">cm</span></div>
                        </div>
                        <div class="sensor-item">
                            <div class="sensor-label">Right Distance</div>
                            <div class="sensor-value" id="right-dist">--<span class="sensor-unit">cm</span></div>
                        </div>
                        <div class="sensor-item">
                            <div class="sensor-label">Temperature</div>
                            <div class="sensor-value" id="temp">--<span class="sensor-unit">°C</span></div>
                        </div>
                        <div class="sensor-item">
                            <div class="sensor-label">Pitch / Roll</div>
                            <div class="sensor-value" style="font-size: 1.2em;" id="orientation">-- / --<span class="sensor-unit">°</span></div>
                        </div>
                    </div>
                </div>
                
                <div class="panel">
                    <h2>🎮 Controls</h2>
                    <div class="controls">
                        <div class="control-pad">
                            <button class="control-btn btn-up" id="btn-forward" title="Forward (↑)">▲</button>
                            <button class="control-btn btn-left" id="btn-left" title="Left (←)">◄</button>
                            <button class="control-btn btn-stop" id="btn-stop" title="Stop (Space)">⏹</button>
                            <button class="control-btn btn-right" id="btn-right" title="Right (→)">►</button>
                            <button class="control-btn btn-down" id="btn-backward" title="Backward (↓)">▼</button>
                        </div>
                        <div class="keyboard-hint">
                            💡 Use arrow keys or W/A/S/D<br>Space to stop
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="info-bar">
            <span id="qr-info">No QR code detected</span>
        </div>
    </div>

    <script>
        // Sensor data polling
        function updateSensors() {
            fetch('/api/sensors')
                .then(response => response.json())
                .then(data => {
                    const statusDot = document.getElementById('status-dot');
                    const statusText = document.getElementById('status-text');
                    
                    if (data.error) {
                        statusDot.classList.add('status-offline');
                        statusText.textContent = 'Sensors Offline';
                        return;
                    }
                    
                    statusDot.classList.remove('status-offline');
                    statusText.textContent = 'Connected';
                    
                    // Update distance sensors
                    updateSensorValue('front-dist', data.front_distance, 40);
                    updateSensorValue('left-dist', data.left_distance, 30);
                    updateSensorValue('right-dist', data.right_distance, 30);
                    
                    // Update IMU data
                    document.getElementById('temp').innerHTML = 
                        (data.temperature || '--') + '<span class="sensor-unit">°C</span>';
                    document.getElementById('orientation').innerHTML = 
                        `${data.pitch || '--'} / ${data.roll || '--'}<span class="sensor-unit">°</span>`;
                    
                    // Update QR info
                    if (data.qr_data) {
                        document.getElementById('qr-info').textContent = '📱 QR: ' + data.qr_data;
                    } else {
                        document.getElementById('qr-info').textContent = 'No QR code detected';
                    }
                })
                .catch(err => {
                    console.error('Sensor update failed:', err);
                    document.getElementById('status-dot').classList.add('status-offline');
                    document.getElementById('status-text').textContent = 'Connection Error';
                });
        }
        
        function updateSensorValue(elementId, value, warningThreshold) {
            const element = document.getElementById(elementId);
            const parent = element.closest('.sensor-item');
            
            if (value === null || value === undefined) {
                element.innerHTML = '--<span class="sensor-unit">cm</span>';
                parent.classList.remove('warning', 'danger');
                return;
            }
            
            const numValue = parseFloat(value);
            element.innerHTML = numValue.toFixed(1) + '<span class="sensor-unit">cm</span>';
            
            parent.classList.remove('warning', 'danger');
            if (numValue < warningThreshold * 0.5) {
                parent.classList.add('danger');
            } else if (numValue < warningThreshold) {
                parent.classList.add('warning');
            }
        }
        
        // Motor control
        function sendCommand(command) {
            fetch('/api/control', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({command: command})
            })
            .then(response => response.json())
            .then(data => {
                if (!data.success) {
                    console.error('Command failed:', data.error);
                }
            })
            .catch(err => console.error('Control error:', err));
        }
        
        // Button event listeners
        document.getElementById('btn-forward').addEventListener('click', () => sendCommand('forward'));
        document.getElementById('btn-backward').addEventListener('click', () => sendCommand('backward'));
        document.getElementById('btn-left').addEventListener('click', () => sendCommand('left'));
        document.getElementById('btn-right').addEventListener('click', () => sendCommand('right'));
        document.getElementById('btn-stop').addEventListener('click', () => sendCommand('stop'));
        
        // Keyboard controls
        const keyMap = {
            'ArrowUp': 'forward',
            'ArrowDown': 'backward',
            'ArrowLeft': 'left',
            'ArrowRight': 'right',
            'w': 'forward',
            'W': 'forward',
            's': 'backward',
            'S': 'backward',
            'a': 'left',
            'A': 'left',
            'd': 'right',
            'D': 'right',
            ' ': 'stop'
        };
        
        let activeKeys = new Set();
        
        document.addEventListener('keydown', (e) => {
            if (keyMap[e.key] && !activeKeys.has(e.key)) {
                e.preventDefault();
                activeKeys.add(e.key);
                sendCommand(keyMap[e.key]);
                
                // Visual feedback
                const btnMap = {
                    'forward': 'btn-forward',
                    'backward': 'btn-backward',
                    'left': 'btn-left',
                    'right': 'btn-right',
                    'stop': 'btn-stop'
                };
                const btn = document.getElementById(btnMap[keyMap[e.key]]);
                if (btn) btn.style.transform = 'scale(0.95)';
            }
        });
        
        document.addEventListener('keyup', (e) => {
            if (keyMap[e.key]) {
                e.preventDefault();
                activeKeys.delete(e.key);
                sendCommand('stop');
                
                // Reset visual feedback
                const btnMap = {
                    'forward': 'btn-forward',
                    'backward': 'btn-backward',
                    'left': 'btn-left',
                    'right': 'btn-right',
                    'stop': 'btn-stop'
                };
                const btn = document.getElementById(btnMap[keyMap[e.key]]);
                if (btn) btn.style.transform = '';
            }
        });
        
        // Start polling sensors
        updateSensors();
        setInterval(updateSensors, 500);  // Update every 500ms
    </script>
</body>
</html>
            ''')

        @self.app.route('/video_feed')
        def video_feed():
            return Response(self._generate_frames(),
                          mimetype='multipart/x-mixed-replace; boundary=frame')
        
        @self.app.route('/api/sensors')
        def api_sensors():
            """Return sensor data as JSON."""
            try:
                data = {
                    'front_distance': None,
                    'left_distance': None,
                    'right_distance': None,
                    'temperature': None,
                    'pitch': None,
                    'roll': None,
                    'yaw': None,
                    'qr_data': None
                }
                
                if self.sensors:
                    try:
                        data['front_distance'] = self.sensors.front.distance
                        data['left_distance'] = self.sensors.left.distance
                        data['right_distance'] = self.sensors.right.distance
                        data['temperature'] = round(self.sensors.mpu.getTemperature(), 1)
                        
                        yaw, pitch, roll = self.sensors.mpu.getYawPitchRoll()
                        data['pitch'] = round(pitch, 1)
                        data['roll'] = round(roll, 1)
                        data['yaw'] = round(yaw, 1)
                    except Exception as e:
                        log.debug('Error reading sensors: %s', e)
                
                # Try to get QR data from camera processor
                if self.camera_worker and hasattr(self.camera_worker, 'processor'):
                    try:
                        if hasattr(self.camera_worker.processor, 'last_qr_data'):
                            data['qr_data'] = self.camera_worker.processor.last_qr_data
                    except Exception:
                        pass
                
                return jsonify(data)
            except Exception as e:
                log.exception('Sensor API error: %s', e)
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/control', methods=['POST'])
        def api_control():
            """Handle motor control commands."""
            try:
                command = request.json.get('command')
                if not command:
                    return jsonify({'success': False, 'error': 'No command specified'}), 400
                
                if not self.motor:
                    return jsonify({'success': False, 'error': 'Motor not available'}), 503
                
                # Execute motor command
                if command == 'forward':
                    self.motor.move_forward()
                elif command == 'backward':
                    self.motor.move_backward()
                elif command == 'left':
                    self.motor.move_left()
                elif command == 'right':
                    self.motor.move_right()
                elif command == 'stop':
                    self.motor.stop()
                else:
                    return jsonify({'success': False, 'error': 'Invalid command'}), 400
                
                log.info('Motor command executed: %s', command)
                return jsonify({'success': True, 'command': command})
            except Exception as e:
                log.exception('Control API error: %s', e)
                return jsonify({'success': False, 'error': str(e)}), 500

    def _generate_frames(self):
        """Generator that yields MJPEG frames."""
        import time
        while not self._stopped:
            frame = self.camera_worker.get_latest_annotated_frame()
            if frame is None:
                time.sleep(0.05)  # Wait for camera to produce frames
                continue
            
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            if not ret:
                time.sleep(0.05)
                continue
            
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(0.033)  # ~30 fps

    def start(self):
        """Start Flask server in a separate thread."""
        log.info('Starting MJPEG streamer on http://%s:%d', self.host, self.port)
        thread = threading.Thread(target=self._run_flask, daemon=True)
        thread.start()
        return thread

    def _run_flask(self):
        self.app.run(host=self.host, port=self.port, debug=False, threaded=True, use_reloader=False)

    def stop(self):
        self._stopped = True
        log.info('MJPEG streamer stopped')
