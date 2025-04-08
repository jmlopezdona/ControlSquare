# ControlSquare

# ControlSquare BLE Connection

Script to connect to a BLE device named "SQUARE" and display button press notifications. It also simulates keyboard key presses in Windows applications when buttons are pressed.

## Requirements

- Python 3.7+
- bleak>=0.21.0
- pynput>=1.7.6
- Windows 11 (tested and verified)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python square_controller.py
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

### Real Value Examples

Below are examples of complete hexadecimal values sent by the device when different buttons are pressed:

| Button | Complete hexadecimal value | Extracted code | Explanation |
|-------|----------------------------|-----------------|-------------|
| Up | 123456000002002020c321e0101 | 00000200 | The first 6 characters (123456) are the timestamp, the next 8 (00000200) identify the "Up" button, and the last 13 (2020c321e0101) are constants |
| Left | 123456000001002020c321e0101 | 00000100 | The code 00000100 identifies the "Left" button |
| X | 123456000020002020c321e0101 | 00002000 | The code 00002000 identifies the "X" button |
| Y | 123456020000002020c321e0101 | 02000000 | The code 02000000 identifies the "Y" button |
| A | 123456010000002020c321e0101 | 01000000 | The code 01000000 identifies the "A" button |

As you can observe, the timestamp changes with each press, but the button code and the final part remain constant for each specific button.

Below is the mapping of buttons and their corresponding button codes (all codes have the same length - 8 characters):

| Button | Button Code | Simulated Key |
|-------|-------------|---------------|
| Up | 00000200 | Up Arrow |
| Left | 00000100 | Left Arrow |
| Down | 00000800 | Down Arrow |
| Right | 00000400 | Right Arrow |
| X | 00002000 | None |
| Square | 00001000 | h |
| Left Campagnolo | 00008000 | c |
| Left brake | 00004000 | 6 |
| Left shift 1 | 00000002 | 1 |
| Left shift 2 | 00000001 | 2 |
| Y | 02000000 | y |
| A | 01000000 | Enter |
| B | 08000000 | Escape |
| Z | 04000000 | z |
| Circle | 20000000 | None |
| Triangle | 10000000 | Space |
| Right Campagnolo | 80000000 | r |
| Right brake | 40000000 | 1 |
| Right shift 1 | 00020000 | 3 |
| Right shift 2 | 00010000 | 4 |

**Note**: Any button code not in this table is considered as "No button pressed".

## Key Simulation

When a button is pressed on the SQUARE device, the script will simulate a keyboard key press in the active Windows application. This allows you to control applications with the SQUARE device.

The key mapping can be customized by modifying the `KEY_MAPPING` dictionary in the `square_controller.py` file.
