# Control Square

Una aplicación Flutter para controlar dispositivos SQUARE a través de Bluetooth.

## Características

- Conexión Bluetooth con dispositivos SQUARE
- Interfaz de usuario intuitiva
- Soporte para todos los botones del dispositivo
- Compatible con Windows 10 y superiores

## Requisitos

- Flutter SDK (versión 3.0.0 o superior)
- Windows 10 o superior
- Bluetooth habilitado en el dispositivo
- Visual Studio 2019 o superior con soporte para desarrollo de Windows
- Microsoft Visual C++ Runtime libraries

## Instalación

1. Instala las dependencias:
```bash
flutter pub get
```

2. Ejecuta la aplicación:
```bash
flutter run -d windows
```

## Uso

1. Asegúrate de que tu dispositivo SQUARE esté encendido y en modo de emparejamiento
2. Abre la aplicación Control Square
3. Haz clic en el icono de Bluetooth en la barra de herramientas
4. Selecciona tu dispositivo SQUARE de la lista
5. Una vez conectado, podrás usar todos los botones del dispositivo

## Mapeo de Botones

El dispositivo SQUARE tiene los siguientes botones mapeados:

- Up: Flecha arriba
- Down: Flecha abajo
- Left: Flecha izquierda
- Right: Flecha derecha
- X: Control izquierdo
- Square: Tecla R
- Left Campagnolo: Flecha izquierda
- Left brake: Tecla 6
- Y: Tecla G
- A: Enter
- B: Escape
- Z: Tecla T
- Circle: Control derecho
- Triangle: Espacio
- Right Campagnolo: Flecha derecha
- Right brake: Tecla 1

## Solución de Problemas

Si tienes problemas para conectar el dispositivo:

1. Asegúrate de que el Bluetooth esté habilitado en tu computadora
2. Verifica que el dispositivo SQUARE esté en modo de emparejamiento
3. Reinicia tanto el dispositivo como la aplicación
4. Asegúrate de tener instaladas las Microsoft Visual C++ Runtime libraries

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.
