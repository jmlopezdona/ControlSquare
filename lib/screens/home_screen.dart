import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_blue_plus/flutter_blue_plus.dart' as flutter_blue;
import '../services/bluetooth_service.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Control Square'),
        actions: [
          Consumer<SquareBluetoothService>(
            builder: (context, bluetoothService, child) {
              return Row(
                children: [
                  Text(
                    bluetoothService.statusMessage,
                    style: const TextStyle(fontSize: 14),
                  ),
                  const SizedBox(width: 8),
                  IconButton(
                    icon: Icon(
                      bluetoothService.isConnected 
                        ? Icons.bluetooth_connected 
                        : bluetoothService.isScanning 
                          ? Icons.bluetooth_searching
                          : Icons.bluetooth,
                      color: bluetoothService.isAvailable 
                        ? bluetoothService.isConnected 
                          ? Colors.green 
                          : Colors.blue
                        : Colors.grey,
                    ),
                    onPressed: bluetoothService.isAvailable
                      ? () {
                          if (bluetoothService.isConnected) {
                            bluetoothService.disconnect();
                          } else if (!bluetoothService.isScanning) {
                            bluetoothService.startScan();
                          }
                        }
                      : null,
                  ),
                ],
              );
            },
          ),
        ],
      ),
      body: Consumer<SquareBluetoothService>(
        builder: (context, bluetoothService, child) {
          if (!bluetoothService.isAvailable) {
            return const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.bluetooth_disabled,
                    size: 64,
                    color: Colors.grey,
                  ),
                  SizedBox(height: 16),
                  Text(
                    'Bluetooth no está disponible',
                    style: TextStyle(fontSize: 18),
                  ),
                  Text(
                    'Por favor, activa el Bluetooth de tu dispositivo',
                    style: TextStyle(fontSize: 14, color: Colors.grey),
                  ),
                ],
              ),
            );
          }

          if (bluetoothService.isScanning) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const CircularProgressIndicator(),
                  const SizedBox(height: 16),
                  Text(
                    bluetoothService.statusMessage,
                    style: const TextStyle(fontSize: 16),
                  ),
                ],
              ),
            );
          }

          if (!bluetoothService.isConnected) {
            if (bluetoothService.scanResults.isEmpty) {
              return Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(
                      Icons.bluetooth_searching,
                      size: 64,
                      color: Colors.blue,
                    ),
                    const SizedBox(height: 16),
                    const Text(
                      'No se encontraron dispositivos',
                      style: TextStyle(fontSize: 18),
                    ),
                    const SizedBox(height: 8),
                    ElevatedButton(
                      onPressed: () => bluetoothService.startScan(),
                      child: const Text('Buscar dispositivos'),
                    ),
                  ],
                ),
              );
            }

            return ListView.builder(
              itemCount: bluetoothService.scanResults.length,
              itemBuilder: (context, index) {
                final result = bluetoothService.scanResults[index];
                final device = result.device;
                
                return ListTile(
                  leading: const Icon(Icons.bluetooth),
                  title: Text(device.platformName.isEmpty 
                    ? 'Dispositivo desconocido'
                    : device.platformName),
                  subtitle: Text(device.remoteId.toString()),
                  trailing: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text('${result.rssi} dBm'),
                      const Icon(Icons.chevron_right),
                    ],
                  ),
                  onTap: () => bluetoothService.connectToDevice(device),
                );
              },
            );
          }

          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const SizedBox(height: 20),
                Text(
                  'Último botón presionado:',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                const SizedBox(height: 10),
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.blue.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    bluetoothService.lastButtonPressed,
                    style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                      color: Colors.blue,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                const SizedBox(height: 20),
                Text(
                  'Nombre: ${bluetoothService.device?.platformName ?? "Desconocido"}',
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                const SizedBox(height: 10),
                Text(
                  'ID: ${bluetoothService.device?.remoteId.toString() ?? "Desconocido"}',
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                const SizedBox(height: 20),
                Text(
                  bluetoothService.statusMessage,
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                const SizedBox(height: 20),
                ElevatedButton(
                  onPressed: () => bluetoothService.disconnect(),
                  child: const Text('Desconectar'),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
} 