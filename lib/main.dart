import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_blue_plus/flutter_blue_plus.dart' as flutter_blue;
import 'package:flutter_blue_plus_windows/flutter_blue_plus_windows.dart';
import 'services/bluetooth_service.dart';
import 'screens/home_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Inicializar FlutterBluePlus
  try {
    print('Iniciando verificación del adaptador Bluetooth...');
    
    // Esperar un momento para que el sistema determine el estado real del Bluetooth
    await Future.delayed(const Duration(seconds: 2));
    
    // Verificar el estado del adaptador
    var adapterState = await FlutterBluePlus.adapterState.first;
    print('Estado inicial del adaptador: $adapterState');
    
    // Si el estado es unknown, esperar a que cambie
    if (adapterState == BluetoothAdapterState.unknown) {
      print('Estado inicial unknown, esperando estado real...');
      adapterState = await FlutterBluePlus.adapterState
          .firstWhere((state) => state != BluetoothAdapterState.unknown);
      print('Estado real del adaptador: $adapterState');
    }
    
    print('Bluetooth inicializado con estado: $adapterState');
  } catch (e) {
    print('Error al verificar el estado del adaptador Bluetooth: $e');
  }
  
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => SquareBluetoothService()),
      ],
      child: MaterialApp(
        title: 'Control Square',
        theme: ThemeData(
          primarySwatch: Colors.blue,
          useMaterial3: true,
        ),
        home: const HomeScreen(),
      ),
    );
  }
} 