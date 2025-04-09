import tkinter as tk
from tkinter import ttk, messagebox
import asyncio
import threading
from square_controller import (
    connect_and_listen, 
    BUTTON_MAPPING, 
    set_message_queue,
    update_key_mapping,
    get_key_mapping,
    Key,
    KeyCode
)
import queue

class KeyConfigWindow:
    def __init__(self, parent, button_name, current_key):
        self.window = tk.Toplevel(parent)
        self.window.title(f"Configurar tecla para {button_name}")
        self.window.geometry("300x150")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.button_name = button_name
        self.current_key = current_key
        self.new_key = None
        
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Etiqueta de instrucciones
        ttk.Label(
            main_frame, 
            text="Presiona la tecla que deseas asignar\no deja en blanco para desactivar",
            justify=tk.CENTER
        ).grid(row=0, column=0, columnspan=2, pady=10)
        
        # Etiqueta para mostrar la tecla actual
        self.current_key_label = ttk.Label(
            main_frame,
            text=f"Tecla actual: {self._format_key(current_key)}"
        )
        self.current_key_label.grid(row=1, column=0, columnspan=2, pady=5)
        
        # Etiqueta para mostrar la nueva tecla
        self.new_key_label = ttk.Label(
            main_frame,
            text="Nueva tecla: "
        )
        self.new_key_label.grid(row=2, column=0, columnspan=2, pady=5)
        
        # Botones
        ttk.Button(
            main_frame,
            text="Cancelar",
            command=self.window.destroy
        ).grid(row=3, column=0, padx=5, pady=10)
        
        ttk.Button(
            main_frame,
            text="Guardar",
            command=self.save_key
        ).grid(row=3, column=1, padx=5, pady=10)
        
        # Bind de teclas
        self.window.bind('<Key>', self.on_key_press)
        self.window.bind('<Escape>', lambda e: self.window.destroy())
        
        # Centrar la ventana
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def _format_key(self, key):
        if key is None:
            return "Ninguna"
        if isinstance(key, Key):
            return key.name
        if isinstance(key, KeyCode):
            return key.char
        return str(key)
    
    def on_key_press(self, event):
        if event.keysym == 'Escape':
            return
        
        if event.keysym in ['Shift_L', 'Shift_R', 'Control_L', 'Control_R', 'Alt_L', 'Alt_R']:
            return
        
        if len(event.keysym) == 1:
            self.new_key = KeyCode.from_char(event.char)
        else:
            try:
                self.new_key = getattr(Key, event.keysym.lower())
            except AttributeError:
                return
        
        self.new_key_label.config(text=f"Nueva tecla: {self._format_key(self.new_key)}")
    
    def save_key(self):
        if self.new_key is not None:
            update_key_mapping(self.button_name, self.new_key)
        self.window.destroy()

class SquareUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Control Square")
        
        # Cola para comunicación entre el hilo BLE y la UI
        self.message_queue = queue.Queue()
        
        # Configurar la cola en el controlador
        set_message_queue(self.message_queue)
        
        # Frame principal
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Estado de conexión
        self.connection_frame = ttk.LabelFrame(main_frame, text="Estado de Conexión", padding="5")
        self.connection_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.connection_status = ttk.Label(self.connection_frame, text="Desconectado", foreground="red")
        self.connection_status.grid(row=0, column=0, padx=5, pady=5)
        
        # Botones detectados
        self.buttons_frame = ttk.LabelFrame(main_frame, text="Botones Detectados", padding="10")
        self.buttons_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Crear etiquetas para cada botón
        self.button_labels = {}
        self.button_frames = {}
        
        # Encontrar el nombre de botón más largo para establecer un ancho fijo
        max_button_name_length = max(len(name) for name in BUTTON_MAPPING.values())
        button_width = max_button_name_length + 2  # Añadir un poco de espacio extra
        
        # Organizar los botones en una cuadrícula
        row = 0
        col = 0
        max_cols = 4  # Número de columnas en la cuadrícula
        
        for button_name in BUTTON_MAPPING.values():
            # Crear un frame para cada botón con borde y padding
            frame = ttk.Frame(self.buttons_frame, style='Button.TFrame')
            frame.grid(row=row, column=col, padx=5, pady=5, sticky=(tk.W, tk.E))
            self.button_frames[button_name] = frame
            
            # Configurar el grid para que se expanda
            frame.columnconfigure(0, weight=1)
            
            # Crear un subframe para el contenido del botón
            content_frame = ttk.Frame(frame)
            content_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
            
            # Nombre del botón con ancho fijo
            label = ttk.Label(
                content_frame, 
                text=button_name, 
                width=button_width,
                anchor=tk.W
            )
            label.grid(row=0, column=0, padx=(5, 10))
            
            # Indicador de estado
            status = ttk.Label(content_frame, text="●", foreground="gray")
            status.grid(row=0, column=1, padx=5)
            
            # Botón de configuración
            config_button = ttk.Button(
                content_frame,
                text="⚙",
                width=3,
                command=lambda btn=button_name: self.configure_key(btn)
            )
            config_button.grid(row=0, column=2, padx=5)
            
            self.button_labels[button_name] = status
            
            # Avanzar a la siguiente posición
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # Log de eventos
        self.log_frame = ttk.LabelFrame(main_frame, text="Registro de Eventos", padding="5")
        self.log_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.log_text = tk.Text(self.log_frame, height=10, width=80)  # Aumentar el ancho del log
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar para el log
        scrollbar = ttk.Scrollbar(self.log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.log_text['yscrollcommand'] = scrollbar.set
        
        # Configurar el grid para que se expanda
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        self.log_frame.columnconfigure(0, weight=1)
        self.log_frame.rowconfigure(0, weight=1)
        
        # Configurar el estilo para los frames de botones
        style = ttk.Style()
        style.configure('Button.TFrame', relief='solid', borderwidth=1)
        
        # Configurar el grid de la ventana principal
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        
        # Ajustar el tamaño de la ventana al contenido
        self.root.update_idletasks()
        self.root.resizable(True, True)
        
        # Iniciar el bucle de actualización de la UI
        self.update_ui()
        
        # Iniciar el hilo BLE
        self.start_ble_thread()
    
    def configure_key(self, button_name):
        current_key = get_key_mapping().get(button_name)
        KeyConfigWindow(self.root, button_name, current_key)
    
    def start_ble_thread(self):
        def run_ble():
            asyncio.run(connect_and_listen())
        
        self.ble_thread = threading.Thread(target=run_ble, daemon=True)
        self.ble_thread.start()
    
    def update_ui(self):
        try:
            while True:
                message = self.message_queue.get_nowait()
                if message.startswith("CONNECTION:"):
                    status = message.split(":")[1]
                    self.connection_status.config(
                        text=status,
                        foreground="green" if "Connected" in status else "red"
                    )
                elif message.startswith("BUTTON:"):
                    button_name = message.split(":")[1]
                    if button_name in self.button_labels:
                        # Cambiar el color del botón a verde
                        self.button_labels[button_name].config(foreground="green")
                        # Programar el cambio de vuelta a gris después de 200ms
                        self.root.after(200, lambda btn=button_name: self.button_labels[btn].config(foreground="gray"))
                
                # Agregar el mensaje al log
                self.log_text.insert(tk.END, message + "\n")
                self.log_text.see(tk.END)
        except queue.Empty:
            pass
        
        # Programar la próxima actualización
        self.root.after(50, self.update_ui)

def main():
    root = tk.Tk()
    app = SquareUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 