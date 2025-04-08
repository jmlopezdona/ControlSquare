# ControlSquare

# ControlSquare BLE Connection

Script to connect to a BLE device named "SQUARE" and display button press notifications. It also simulates keyboard key presses in Windows applications when buttons are pressed.

## Requirements

- Python 3.7+
- bleak>=0.21.0
- pynput>=1.7.6

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python ble_connection.py
```

## BLE Characteristics

The button values are obtained from the following BLE characteristic:
- Characteristic UUID: `347b0043-7635-408b-8918-8ff3949ce592`

## Button Mapping

The device sends a hexadecimal value for each button press. This value contains several parts:
- The first 6 characters appear to be a timestamp
- The middle part contains the button code (8 characters)
- The final part ("2020c321e0101") appears to be constant

The script uses a simplified approach to extract the button code:
1. It skips the first 6 characters (timestamp)
2. It then extracts exactly 8 characters as the button code

### Ejemplos de valores reales

A continuación se muestran ejemplos de valores hexadecimales completos que el dispositivo envía cuando se presionan diferentes botones:

| Botón | Valor hexadecimal completo | Código extraído | Explicación |
|-------|----------------------------|-----------------|-------------|
| Up | 123456000002002020c321e0101 | 00000200 | Los primeros 6 caracteres (123456) son el timestamp, los siguientes 8 (00000200) identifican el botón "Up", y los últimos 13 (2020c321e0101) son constantes |
| Left | 123456000001002020c321e0101 | 00000100 | El código 00000100 identifica el botón "Left" |
| X | 123456000020002020c321e0101 | 00002000 | El código 00002000 identifica el botón "X" |
| Y | 123456000000022020c321e0101 | 00000002 | El código 00000002 identifica el botón "Y" |
| A | 123456000000012020c321e0101 | 00000001 | El código 00000001 identifica el botón "A" |

Como se puede observar, el timestamp cambia en cada pulsación, pero el código del botón y la parte final permanecen constantes para cada botón específico.

Below is the mapping of buttons and their corresponding button codes (all codes have the same length - 8 characters):

| Button | Button Code | Simulated Key |
|-------|-------------|---------------|
| Up | 00000200 | Up Arrow |
| Left | 00000100 | Left Arrow |
| Down | 00000800 | Down Arrow |
| Right | 00000400 | Right Arrow |
| X | 00002000 | x |
| Square | 00001000 | s |
| Left Campagnolo | 00008000 | c |
| Left brake | 00004000 | b |
| Left shift 1 | 00000002 | 1 |
| Left shift 2 | 00000001 | 2 |
| Y | 00000002 | y |
| A | 00000001 | a |
| B | 00000008 | b |
| Z | 00000004 | z |
| Circle | 00000020 | o |
| Triangle | 00000010 | t |
| Right Campagnolo | 00000080 | r |
| Right brake | 00000040 | b |
| Right shift 1 | 00000002 | 3 |
| Right shift 2 | 00000001 | 4 |

**Note**: Any button code not in this table is considered as "No button pressed".

## Key Simulation

When a button is pressed on the SQUARE device, the script will simulate a keyboard key press in the active Windows application. This allows you to control applications with the SQUARE device.

The key mapping can be customized by modifying the `KEY_MAPPING` dictionary in the `ble_connection.py` file.
