# RaspiTankPy-Extended

Progetto per controllare un tank robot su Raspberry Pi 4 con sensori I2C e camera.
Si basa sull'approccio multithreaded della repo di riferimento https://github.com/manfredipist/RaspiTankPy e aggiunge:

- wrapper hardware-optional per VL53L1X (laser) e MPU6050 (IMU)
- pipeline OpenCV per visualizzazione, rilevamento ostacoli e decodifica QR
- display via X11 (compatibile con XQuartz quando si usa forwarding X11)
- **streaming MJPEG via Flask** per visualizzare il video nel browser senza X11
- watchdog di sicurezza che ferma i motori in caso di sensori non funzionanti o ostacolo ravvicinato

## Struttura del Progetto

```
raspi_tank/
├── config.py              # Configurazione globale
├── controller.py          # Watchdog e logica di sicurezza
├── motors/                # Controllo motori
│   ├── motor.py          # Classe Motor con GPIO
│   └── README.md
├── sensors/               # Sensori I2C
│   ├── laser.py          # VL53L1X wrapper
│   ├── accgyro.py        # MPU6050 wrapper
│   ├── i2c_multiplexer.py # TCA9548A manager
│   └── README.md
├── vision/                # Acquisizione e processing video
│   ├── camera.py         # CameraWorker thread
│   ├── processor.py      # OpenCV processing (QR, obstacles)
│   └── README.md
└── streaming/             # Interfaccia web e streaming
    ├── mjpeg_streamer.py # Flask server con API REST
    └── README.md
```

## Prerequisiti e installazione

1. Abilitare I2C su Raspberry Pi (raspi-config).
2. Installare XQuartz su macOS per visualizzare le finestre via SSH X11 forwarding (opzionale se si usa streaming web o VNC/monitor locale).
3. Installare dipendenze Python:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Uso

### Modalità 1: Streaming Web con Controllo Completo (consigliato)

1. Modifica `raspi_tank/config.py` e assicurati che:
   ```python
   camera = {
       'enable_mjpeg_stream': True,
       'stream_host': '0.0.0.0',
       'stream_port': 5000,
       'show_window': False  # disabilita cv2.imshow per evitare errori se no X11
   }
   ```

2. Avvia il programma sul Raspberry Pi:
   ```bash
   python3 main.py
   ```

3. Apri il browser su qualsiasi dispositivo nella stessa rete e vai a:
   ```
   http://<ip-raspberry-pi>:5000
   ```

**Funzionalità dell'interfaccia web:**
- 📹 **Video live** con overlay OpenCV (QR detection, ostacoli, edges)
- 📡 **Dati sensori in tempo reale:**
  - Distanze laser (front/left/right) con indicatori di pericolo colorati
  - Temperatura IMU
  - Orientamento (pitch/roll)
  - Decodifica QR code
- 🎮 **Controlli robot:**
  - Pulsanti direzionali cliccabili
  - Supporto tastiera: frecce direzionali o W/A/S/D
  - Spazio per stop immediato
  - Feedback visivo in tempo reale

**Codici colore sensori:**
- 🟢 Verde: distanza sicura
- 🟠 Arancione: attenzione (< soglia)
- 🔴 Rosso: pericolo (< 50% soglia)

### Modalità 2: Display X11 via XQuartz (macOS)

1. Modifica `raspi_tank/config.py`:
   ```python
   camera = {
       'show_window': True,
       'enable_mjpeg_stream': False  # opzionale
   }
   ```

2. Avvia XQuartz sul Mac.

3. Connetti via SSH con X11 forwarding:
   ```bash
   ssh -X pi@raspberrypi
   ```

4. Avvia il programma:
   ```bash
   python3 main.py
   ```
   La finestra OpenCV apparirà su XQuartz. Premi 'q' nella finestra video per chiudere.

### Modalità 3: Entrambe (streaming + X11)

Imposta entrambi `show_window: True` e `enable_mjpeg_stream: True` in `config.py` per avere sia la finestra locale che lo streaming web simultaneamente.

## Note

- Il codice è hardware-aware: se le librerie adafruit non sono installate o l'hardware non è presente, i sensori useranno stub che simulano valori (così è possibile eseguire test in sviluppo).
- File di configurazione in `raspi_tank/config.py`.
- Lo streaming MJPEG usa Flask ed è accessibile da qualsiasi browser sulla stessa rete.

## Comportamento di sicurezza

Il watchdog monitora continuamente:
- **Timeout sensori**: se i sensori non si aggiornano per più di 2.5s (configurabile), i motori vengono fermati.
- **Ostacoli frontali**: se la distanza frontale scende sotto 40cm (configurabile), i motori si arrestano automaticamente.

## Test

### Test completo con interfaccia web (no hardware richiesto):
```bash
python3 demo_streaming.py
```
Poi vai su `http://localhost:5000` per vedere:
- Video simulato con pattern di test
- Sensori simulati con valori casuali
- Controlli motore funzionanti (console log)
- Interfaccia completa come su Raspberry Pi

### Test unitari:
```bash
pip install pytest
pytest -q
```

## Contribuire

Segnala issue o PR per migliorare sensori, gestione motori o streaming video.
