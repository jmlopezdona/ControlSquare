# ControlSquare

A Flutter application for controlling the SQUARE device via Bluetooth.

## Features

- Automatic Bluetooth device discovery and connection
- Real-time button press detection
- Resilient connection with automatic reconnection
- Support for Windows platform
- Clean and intuitive user interface

## Supported Buttons

The application recognizes the following buttons from the SQUARE device:

- **Navigation**: Up, Down, Left, Right
- **Action Buttons**: X, Y, A, B, Z, Square, Circle, Triangle
- **Shift Controls**: Left shift 1, Left shift 2, Right shift 1, Right shift 2
- **Brake Controls**: Left brake, Right brake
- **Special Controls**: Left Campagnolo, Right Campagnolo

## Requirements

- Flutter SDK (>=3.0.0)
- Windows 10 or later
- Bluetooth adapter
- SQUARE device

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/control_square.git
   ```

2. Navigate to the project directory:
   ```
   cd control_square
   ```

3. Install dependencies:
   ```
   flutter pub get
   ```

4. Run the application:
   ```
   flutter run -d windows
   ```

## How It Works

1. The application automatically initializes the Bluetooth service on startup
2. It continuously scans for the SQUARE device
3. When found, it automatically connects to the device
4. The application listens for button presses and displays them in real-time
5. If the connection is lost, it automatically attempts to reconnect

## Dependencies

- `flutter_blue_plus`: ^1.31.13
- `flutter_blue_plus_windows`: ^1.26.1
- `provider`: ^6.1.1

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to the Flutter team for the amazing framework
- Thanks to the flutter_blue_plus team for the Bluetooth implementation
