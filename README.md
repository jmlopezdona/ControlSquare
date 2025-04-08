# ControlSquare

# ControlSquare BLE Connection

Script to connect to a BLE device named "SQUARE" and display button press notifications.

## Requirements

- Python 3.7+
- bleak>=0.21.0

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

Below is the mapping of buttons and their corresponding hexadecimal values:

| Button | Hexadecimal Value |
|-------|------------------|
| Up | 0201610000020002020c321e0101 |
| Left | 0201610000010002020c321e0101 |
| Down | 0201610000080002020c321e0101 |
| Right | 0201610000040002020c321e0101 |
| X | 0201610000200002020c321e0101 |
| Square | 0201610000100002020c321e0101 |
| Left Campagnolo | 0201610000800002020c321e0101 |
| Left brake | 0201610000400002020c321e0101 |
| Left shift 1 | 0201610000000202020c321e0101 |
| Left shift 2 | 0201610000000102020c321e0101 |
| Y | 0201610200000002020c321e0101 |
| A | 0201610100000002020c321e0101 |
| B | 0201610800000002020c321e0101 |
| Z | 0201610400000002020c321e0101 |
| Circle | 0201612000000002020c321e0101 |
| Triangle | 0201611000000002020c321e0101 |
| Right Campagnolo | 0201618000000002020c321e0101 |
| Right brake | 0201614000000002020c321e0101 |
| Right shift 1 | 0201610002000002020c321e0101 |
| Right shift 2 | 0201610001000002020c321e0101 |

**Note**: Any hexadecimal value not in this table is considered as "No button pressed".
