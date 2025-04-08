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
  String _statusMessage = 'Inicializando...';
  String _lastButtonPressed = 'Ninguno';
  List<ScanResult> _scanResults = [];

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

  Future<void> _initBluetooth() async {
    try {
      print('Iniciando inicialización de Bluetooth...');
      
      // Esperar un momento para que el sistema determine el estado real del Bluetooth
      await Future.delayed(const Duration(seconds: 2));
      
      // Verificar si el Bluetooth está disponible
      var adapterState = await FlutterBluePlus.adapterState.first;
      print('Estado del adaptador Bluetooth: $adapterState');
      
      // Si el estado es unknown, intentar obtener el estado real
      if (adapterState == BluetoothAdapterState.unknown) {
        print('Estado inicial unknown, esperando estado real...');
        // Esperar a que el estado cambie de unknown
        adapterState = await FlutterBluePlus.adapterState
            .firstWhere((state) => state != BluetoothAdapterState.unknown);
        print('Estado real del adaptador: $adapterState');
      }
      
      _isAvailable = adapterState == BluetoothAdapterState.on;
      print('¿Bluetooth disponible? $_isAvailable');
      
      if (!_isAvailable) {
        _statusMessage = 'Bluetooth no está activado';
        print('Bluetooth no está disponible. Estado actual: $adapterState');
        notifyListeners();
        return;
      }

      _statusMessage = 'Bluetooth listo';
      print('Bluetooth inicializado correctamente');
      notifyListeners();

      // Escuchar cambios en el estado del adaptador Bluetooth
      FlutterBluePlus.adapterState.listen((state) {
        print('Cambio en el estado del adaptador: $state');
        _isAvailable = state == BluetoothAdapterState.on;
        _statusMessage = _isAvailable ? 'Bluetooth listo' : 'Bluetooth no está activado';
        print('Estado actualizado - Disponible: $_isAvailable, Mensaje: $_statusMessage');
        notifyListeners();
      });

    } catch (e) {
      print('Error al inicializar Bluetooth: $e');
      _statusMessage = 'Error al inicializar Bluetooth: $e';
      _isAvailable = false;
      notifyListeners();
    }
  }

  Future<void> startScan() async {
    if (!_isAvailable) {
      _statusMessage = 'Bluetooth no está disponible';
      notifyListeners();
      return;
    }

    try {
      _isScanning = true;
      _statusMessage = 'Buscando dispositivos...';
      _scanResults = [];
      notifyListeners();

      await FlutterBluePlus.startScan(
        timeout: const Duration(seconds: 4),
      );
      
      FlutterBluePlus.scanResults.listen((results) {
        _scanResults = results;
        _statusMessage = 'Dispositivos encontrados: ${results.length}';
        notifyListeners();
      });

      await Future.delayed(const Duration(seconds: 4));
      await FlutterBluePlus.stopScan();
      _isScanning = false;
      _statusMessage = _scanResults.isEmpty ? 'No se encontraron dispositivos' : 'Selecciona un dispositivo';
      notifyListeners();
    } catch (e) {
      _isScanning = false;
      _statusMessage = 'Error al escanear: $e';
      notifyListeners();
    }
  }

  Future<void> connectToDevice(BluetoothDevice device) async {
    try {
      _statusMessage = 'Conectando a ${device.platformName}...';
      notifyListeners();

      _device = device;
      await device.connect(timeout: const Duration(seconds: 4));
      _isConnected = true;
      _statusMessage = 'Conectado a ${device.platformName}';
      notifyListeners();

      // Discover services
      _statusMessage = 'Buscando servicios...';
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
            _statusMessage = 'Listo para recibir comandos';
            notifyListeners();
            break;
          }
        }
      }
    } catch (e) {
      _statusMessage = 'Error al conectar: $e';
      _isConnected = false;
      _device = null;
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
      if (_device != null) {
        await _device!.disconnect();
      }
      _isConnected = false;
      _device = null;
      _characteristic = null;
      notifyListeners();
    } catch (e) {
      print('Error disconnecting: $e');
    }
  }
} 