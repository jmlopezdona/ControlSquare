import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter_blue_plus/flutter_blue_plus.dart' hide FlutterBluePlus;
import 'package:flutter_blue_plus_windows/flutter_blue_plus_windows.dart';

class SquareBluetoothService extends ChangeNotifier {
  static const String DEVICE_NAME = "SQUARE";
  static const String CHARACTERISTIC_UUID = "347b0043-7635-408b-8918-8ff3949ce592";
  
  BluetoothDevice? _device;
  BluetoothCharacteristic? _characteristic;
  bool _isConnected = false;
  bool _isScanning = false;
  bool _isAvailable = false;
  String _statusMessage = 'Initializing...';
  String _lastButtonPressed = 'None';
  List<ScanResult> _scanResults = [];
  
  // Variables for reconnection
  Timer? _reconnectTimer;
  Timer? _rescanTimer;
  int _reconnectAttempts = 0;
  static const int MAX_RECONNECT_ATTEMPTS = 5;
  static const Duration RECONNECT_DELAY = Duration(seconds: 3);
  static const Duration RESCAN_DELAY = Duration(seconds: 5);

  // Button mapping (all codes have the same length - 8 characters)
  final Map<String, String> buttonMapping = {
    "00000200": "Up",
    "00000100": "Left",
    "00000800": "Down",
    "00000400": "Right",
    "00002000": "X",
    "00001000": "Square",
    "00008000": "Left Campagnolo",
    "00004000": "Left brake",
    "00000002": "Left shift 1",
    "00000001": "Left shift 2",
    "02000000": "Y",
    "01000000": "A",
    "08000000": "B",
    "04000000": "Z",
    "20000000": "Circle",
    "10000000": "Triangle",
    "80000000": "Right Campagnolo",
    "40000000": "Right brake",
    "00020000": "Right shift 1",
    "00010000": "Right shift 2"
  };

  // Getters
  bool get isConnected => _isConnected;
  bool get isScanning => _isScanning;
  bool get isAvailable => _isAvailable;
  String get statusMessage => _statusMessage;
  String get lastButtonPressed => _lastButtonPressed;
  List<ScanResult> get scanResults => _scanResults;
  BluetoothDevice? get device => _device;

  SquareBluetoothService() {
    _initBluetooth();
  }

  @override
  void dispose() {
    _reconnectTimer?.cancel();
    _rescanTimer?.cancel();
    disconnect();
    super.dispose();
  }

  Future<void> _initBluetooth() async {
    try {
      print('Starting Bluetooth initialization...');
      
      // Wait a moment for the system to determine the real Bluetooth state
      await Future.delayed(const Duration(seconds: 2));
      
      // Check if Bluetooth is available
      var adapterState = await FlutterBluePlus.adapterState.first;
      print('Bluetooth adapter state: $adapterState');
      
      // If state is unknown, try to get the real state
      if (adapterState == BluetoothAdapterState.unknown) {
        print('Initial state unknown, waiting for real state...');
        // Wait for the state to change from unknown
        adapterState = await FlutterBluePlus.adapterState
            .firstWhere((state) => state != BluetoothAdapterState.unknown);
        print('Real adapter state: $adapterState');
      }
      
      _isAvailable = adapterState == BluetoothAdapterState.on;
      print('Is Bluetooth available? $_isAvailable');
      
      if (!_isAvailable) {
        _statusMessage = 'Bluetooth is not activated';
        print('Bluetooth is not available. Current state: $adapterState');
        notifyListeners();
        return;
      }

      _statusMessage = 'Bluetooth ready';
      print('Bluetooth initialized correctly');
      notifyListeners();

      // Listen for changes in the Bluetooth adapter state
      FlutterBluePlus.adapterState.listen((state) {
        print('Adapter state changed: $state');
        _isAvailable = state == BluetoothAdapterState.on;
        _statusMessage = _isAvailable ? 'Bluetooth ready' : 'Bluetooth is not activated';
        print('State updated - Available: $_isAvailable, Message: $_statusMessage');
        
        // If Bluetooth is available, start scanning automatically
        if (_isAvailable && !_isConnected && !_isScanning) {
          print('Starting automatic scan...');
          startScan();
        }
        
        notifyListeners();
      });

      // Start the first scan if Bluetooth is available
      if (_isAvailable && !_isConnected && !_isScanning) {
        print('Starting first scan...');
        startScan();
      }

    } catch (e) {
      print('Error initializing Bluetooth: $e');
      _statusMessage = 'Error initializing Bluetooth: $e';
      _isAvailable = false;
      notifyListeners();
      
      // Schedule a retry of initialization
      _scheduleRescan();
    }
  }

  void _scheduleRescan() {
    _rescanTimer?.cancel();
    _rescanTimer = Timer(RESCAN_DELAY, () {
      print('Retrying Bluetooth initialization...');
      _initBluetooth();
    });
  }

  void _scheduleReconnect() {
    _reconnectTimer?.cancel();
    _reconnectAttempts++;
    
    if (_reconnectAttempts <= MAX_RECONNECT_ATTEMPTS) {
      print('Scheduling reconnection in ${RECONNECT_DELAY.inSeconds} seconds (attempt $_reconnectAttempts of $MAX_RECONNECT_ATTEMPTS)');
      _statusMessage = 'Reconnecting in ${RECONNECT_DELAY.inSeconds} seconds...';
      notifyListeners();
      
      _reconnectTimer = Timer(RECONNECT_DELAY, () {
        if (_device != null) {
          print('Attempting to reconnect to device ${_device!.platformName}...');
          connectToDevice(_device!);
        } else {
          print('Device not available, starting new scan...');
          startScan();
        }
      });
    } else {
      print('Maximum reconnection attempts reached, starting new scan...');
      _reconnectAttempts = 0;
      startScan();
    }
  }

  Future<void> startScan() async {
    if (!_isAvailable) {
      _statusMessage = 'Bluetooth is not available';
      notifyListeners();
      return;
    }

    try {
      _isScanning = true;
      _statusMessage = 'Searching for SQUARE device...';
      _scanResults = [];
      notifyListeners();

      await FlutterBluePlus.startScan(
        timeout: const Duration(seconds: 10),
      );
      
      FlutterBluePlus.scanResults.listen((results) {
        _scanResults = results;
        
        // Look for the SQUARE device
        for (var result in results) {
          if (result.device.platformName == DEVICE_NAME) {
            print('SQUARE device found, connecting...');
            _statusMessage = 'SQUARE device found, connecting...';
            notifyListeners();
            
            // Stop scanning and connect
            FlutterBluePlus.stopScan();
            connectToDevice(result.device);
            return;
          }
        }
        
        _statusMessage = 'Devices found: ${results.length}';
        notifyListeners();
      });

      await Future.delayed(const Duration(seconds: 10));
      await FlutterBluePlus.stopScan();
      _isScanning = false;
      
      if (!_isConnected) {
        _statusMessage = 'SQUARE device not found';
        // Schedule a new scan
        _scheduleRescan();
      }
      
      notifyListeners();
    } catch (e) {
      _isScanning = false;
      _statusMessage = 'Error scanning: $e';
      notifyListeners();
      
      // Schedule a new scan
      _scheduleRescan();
    }
  }

  Future<void> connectToDevice(BluetoothDevice device) async {
    try {
      _statusMessage = 'Connecting to ${device.platformName}...';
      notifyListeners();

      _device = device;
      await device.connect(timeout: const Duration(seconds: 4));
      _isConnected = true;
      _reconnectAttempts = 0; // Reset attempt counter
      _statusMessage = 'Connected to ${device.platformName}';
      notifyListeners();

      // Set up listener for disconnection
      device.connectionState.listen((BluetoothConnectionState state) {
        print('Connection state changed: $state');
        if (state == BluetoothConnectionState.disconnected) {
          _isConnected = false;
          _statusMessage = 'Device disconnected';
          notifyListeners();
          
          // Schedule reconnection
          _scheduleReconnect();
        }
      });

      // Discover services
      _statusMessage = 'Searching for services...';
      notifyListeners();
      
      List<BluetoothService> services = await device.discoverServices();
      for (var service in services) {
        for (var characteristic in service.characteristics) {
          if (characteristic.uuid.toString() == CHARACTERISTIC_UUID) {
            _characteristic = characteristic;
            await characteristic.setNotifyValue(true);
            characteristic.value.listen((value) {
              _handleNotification(value);
            });
            _statusMessage = 'Ready to receive commands';
            notifyListeners();
            break;
          }
        }
      }
    } catch (e) {
      print('Error connecting: $e');
      _statusMessage = 'Error connecting: $e';
      _isConnected = false;
      
      // Schedule reconnection
      _scheduleReconnect();
      
      notifyListeners();
    }
  }

  void _handleNotification(List<int> value) {
    if (value.isEmpty) return;

    // Convert bytes to hex string
    String hexValue = value.map((byte) => byte.toRadixString(16).padLeft(2, '0')).join();
    
    // Extract button code (8 characters after timestamp)
    if (hexValue.length >= 14) {
      String buttonCode = hexValue.substring(6, 14);
      String? buttonName = buttonMapping[buttonCode];
      
      if (buttonName != null) {
        print('Button pressed: $buttonName');
        _lastButtonPressed = buttonName;
        notifyListeners();
      }
    }
  }

  Future<void> disconnect() async {
    try {
      _reconnectTimer?.cancel();
      _rescanTimer?.cancel();
      
      if (_device != null) {
        await _device!.disconnect();
      }
      _isConnected = false;
      _device = null;
      _characteristic = null;
      _reconnectAttempts = 0;
      notifyListeners();
    } catch (e) {
      print('Error disconnecting: $e');
    }
  }
} 