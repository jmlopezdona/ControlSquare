# ControlSquare

This project enables Bluetooth connectivity with the Elite Square device, allowing you to subscribe to button press notifications and simulate keyboard shortcuts in indoor cycling applications such as Zwift, MyWhoosh, and TrainingPeaks Virtual.

Currently, the Elite Square device only allows steering control in Zwift using the X and Circle buttons, while the remaining buttons have no functionality. This Python script extends the device's capabilities by enabling all buttons to be used for menu navigation and other controls.

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

Button values are obtained from the following BLE characteristic:
- Device Name: `SQUARE`
- Service UUID: `347b0001-7635-408b-8918-8ff3949ce592`
- Characteristic UUID: `347b0043-7635-408b-8918-8ff3949ce592`

## Button Mapping

The device sends a hexadecimal value for each button press. The button identification is based on a specific 8-character section within this value. The rest of the hexadecimal string contains additional data that is not relevant for button identification.

### Real Value Examples

Below are examples of complete hexadecimal values sent by the device when different buttons are pressed:

| Button | Complete hexadecimal value | Extracted code | Explanation |
|-------|----------------------------|-----------------|-------------|
| Up | 123456000002002020c321e0101 | 00000200 | The 8-character code 00000200 identifies the "Up" button |
| Left | 123456000001002020c321e0101 | 00000100 | The 8-character code 00000100 identifies the "Left" button |
| X | 123456000020002020c321e0101 | 00002000 | The 8-character code 00002000 identifies the "X" button |
| Y | 123456020000002020c321e0101 | 02000000 | The 8-character code 02000000 identifies the "Y" button |
| A | 123456010000002020c321e0101 | 01000000 | The 8-character code 01000000 identifies the "A" button |

Below is the mapping of buttons and their corresponding button codes (all codes have the same length - 8 characters):

| Button | Button Code | Simulated Key | Zwift Functionality |
|-------|-------------|---------------|---------------------|
| Up | 00000200 | Up Arrow | Navigate up in menus |
| Left | 00000100 | Left Arrow | Navigate left in menus |
| Down | 00000800 | Down Arrow | Navigate down in menus |
| Right | 00000400 | Right Arrow | Navigate right in menus |
| X | 00002000 | None | Left steering control (default; you need pairing Square in Zwift) |
| Square | 00001000 | h | Toggle HUD |
| Left Campagnolo | 00008000 | Left Arrow| Navigate left |
| Left brake | 00004000 | Toggles '6'/'1' | Toggles backward/forward camera view |
| Left shift 1 | 00000002 | None | (Reserved for virtual gears) |
| Left shift 2 | 00000001 | None | (Reserved for virtual gears) |
| Y | 02000000 | g | Alternate power and watts and FC view |
| A | 01000000 | Enter | Confirm selection |
| B | 08000000 | Escape | Cancel/back |
| Z | 04000000 | t | Garage screen |
| Circle | 20000000 | None | Rigth steering control (default; you need pairing Square in Zwift) |
| Triangle | 10000000 | Space | Activate powerup |
| Right Campagnolo | 80000000 | Rigth Arrow | Navigate Right |
| Right brake | 40000000 | None | No view change function |
| Right shift 1 | 00020000 | None | (Reserved for virtual gears) |
| Right shift 2 | 00010000 | None | (Reserved for virtual gears) |

**Note**: Any button code not listed in this table is considered as "No button pressed".

## Key Simulation

When a button is pressed on the SQUARE device, the script simulates a keyboard key press in the active Windows application. This enables you to control applications using the SQUARE device.

The key mapping can be customized by modifying the `KEY_MAPPING` dictionary in the `square_controller.py` file.
