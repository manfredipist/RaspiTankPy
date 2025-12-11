# Streaming Package

Modulo per lo streaming video e l'interfaccia web di controllo.

## Componenti

### `mjpeg_streamer.py`
Classe `MJPEGStreamer` che gestisce:
- Server Flask per interfaccia web
- Streaming MJPEG del video
- API REST per sensori e controllo
- Interfaccia HTML/JavaScript completa

## Funzionalità

### Video Streaming
- Streaming MJPEG in tempo reale
- Qualità JPEG configurabile (default 85%)
- Supporto multi-viewer

### API Endpoints

#### `GET /`
Interfaccia web principale con:
- Video live
- Pannello sensori in tempo reale
- Controlli robot (pulsanti + tastiera)

#### `GET /video_feed`
Stream MJPEG del video

#### `GET /api/sensors`
Ritorna JSON con dati sensori:
```json
{
  "front_distance": 80.5,
  "left_distance": 120.3,
  "right_distance": 110.2,
  "temperature": 25.4,
  "pitch": -2.3,
  "roll": 1.8,
  "yaw": 0.5,
  "qr_data": "DETECTED_QR_CODE"
}
```

#### `POST /api/control`
Invia comandi motore:
```json
{"command": "forward"}
```
Comandi: `forward`, `backward`, `left`, `right`, `stop`

## Configurazione

In `raspi_tank/config.py`:
```python
camera = {
    'enable_mjpeg_stream': True,
    'stream_host': '0.0.0.0',
    'stream_port': 5000
}
```

## Uso

```python
from raspi_tank.streaming import MJPEGStreamer

streamer = MJPEGStreamer(
    camera_worker,
    sensors=sensor_mux,
    motor=motor_instance,
    host='0.0.0.0',
    port=5000
)
streamer.start()
```

Accedi all'interfaccia su `http://<raspberry-pi-ip>:5000`
