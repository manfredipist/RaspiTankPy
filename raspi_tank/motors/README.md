# Motors Package

Modulo per il controllo dei motori del robot.

## Componenti

### `motor.py`
Classe `Motor` che gestisce il controllo dei motori DC tramite GPIO.

**Metodi:**
- `move_forward()` - Movimento in avanti
- `move_backward()` - Movimento indietro
- `move_left()` - Rotazione sinistra
- `move_right()` - Rotazione destra
- `stop()` - Arresto motori

**Hardware-aware:** Se RPi.GPIO non è disponibile, i comandi vengono solo loggati (utile per sviluppo su Mac/PC).

## Configurazione

I pin GPIO sono definiti in `raspi_tank/config.py`:
```python
motor = {
    'left_pins': {'en':13, 'in_1':26, 'in_2':19},
    'right_pins': {'en':21, 'in_1':16, 'in_2':20}
}
```

## Uso

```python
from raspi_tank.motors import Motor

motor = Motor()
motor.move_forward()
time.sleep(1)
motor.stop()
```
