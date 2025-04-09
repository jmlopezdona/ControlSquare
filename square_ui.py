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

# Definir categorías de botones como secciones de un mando
BUTTON_CATEGORIES = {
    "Cruceta": ["Up", "Down", "Left", "Right"],
    "Botones de Acción": ["A", "B", "X", "Y"],
    "Gatillos": ["Left brake", "Right brake"],
    "Cambios": ["Left shift 1", "Left shift 2", "Right shift 1", "Right shift 2"],
    "Botones Especiales": ["Square", "Circle", "Triangle", "Z"],
    "Campagnolo": ["Left Campagnolo", "Right Campagnolo"]
}

# Colores para la interfaz
COLORS = {
    "bg": "#ffffff",
    "fg": "#000000",
    "button_bg": "#f0f0f0",
    "button_fg": "#000000",
    "frame_bg": "#ffffff",
    "frame_fg": "#000000",
    "status_connected": "#008000",
    "status_disconnected": "#ff0000",
    "button_pressed": "#00ff00",
    "button_normal": "#808080",
    "log_bg": "#ffffff",
    "log_fg": "#000000"
}

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
        
        # Aplicar colores
        self.window.configure(bg=COLORS["bg"])
        
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

class GlobalConfigWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Configuración de Teclas")
        self.window.transient(parent)
        self.window.grab_set()
        
        # Aplicar colores
        self.window.configure(bg=COLORS["bg"])
        
        # Frame principal con scrollbar
        main_frame = ttk.Frame(self.window)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Canvas y Scrollbar
        canvas = tk.Canvas(main_frame, bg=COLORS["bg"])
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        # Configurar el scrolling
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Crear ventana en el canvas
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=canvas.winfo_reqwidth())
        
        # Configurar el canvas para que se expanda
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Configurar el scrolling con el ratón
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        # Título
        ttk.Label(
            scrollable_frame, 
            text="Configuración de Teclas para Control Square",
            font=("Arial", 12, "bold"),
            justify=tk.CENTER
        ).grid(row=0, column=0, columnspan=4, pady=10)
        
        # Instrucciones
        ttk.Label(
            scrollable_frame, 
            text="Haz clic en una celda y presiona la tecla que deseas asignar.\nDeja en blanco para desactivar la tecla.",
            justify=tk.CENTER
        ).grid(row=1, column=0, columnspan=4, pady=5)
        
        # Frame para la tabla de configuración
        table_frame = ttk.Frame(scrollable_frame)
        table_frame.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Centrar el contenido de la tabla
        table_frame.columnconfigure(0, weight=1)
        table_frame.columnconfigure(1, weight=1)
        table_frame.columnconfigure(2, weight=1)
        table_frame.columnconfigure(3, weight=1)
        
        # Crear encabezados de la tabla
        ttk.Label(table_frame, text="Botón", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Label(table_frame, text="Tecla Asignada", font=("Arial", 10, "bold")).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        ttk.Label(table_frame, text="Botón", font=("Arial", 10, "bold")).grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        ttk.Label(table_frame, text="Tecla Asignada", font=("Arial", 10, "bold")).grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        
        # Obtener todas las asignaciones actuales
        current_mappings = get_key_mapping()
        
        # Crear filas para cada botón
        self.key_entries = {}
        
        # Calcular el número total de botones para dividir en dos columnas
        total_buttons = sum(len(buttons) for buttons in BUTTON_CATEGORIES.values())
        buttons_per_column = (total_buttons + 1) // 2  # Redondear hacia arriba
        
        # Contador para saber cuándo cambiar de columna
        button_count = 0
        
        # Contador de filas para cada columna
        left_row = 1
        right_row = 1
        
        for category, buttons in BUTTON_CATEGORIES.items():
            # Etiqueta de categoría
            if button_count < buttons_per_column:
                # Primera columna
                ttk.Label(
                    table_frame, 
                    text=category,
                    font=("Arial", 10, "bold")
                ).grid(row=left_row, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
                left_row += 1
            else:
                # Segunda columna
                ttk.Label(
                    table_frame, 
                    text=category,
                    font=("Arial", 10, "bold")
                ).grid(row=right_row, column=2, columnspan=2, sticky=tk.W, pady=(10, 5))
                right_row += 1
            
            # Botones de esta categoría
            for button_name in buttons:
                if button_name in BUTTON_MAPPING.values():
                    # Determinar en qué columna va este botón
                    if button_count < buttons_per_column:
                        # Primera columna
                        col_offset = 0
                        current_row = left_row
                        left_row += 1
                    else:
                        # Segunda columna
                        col_offset = 2
                        current_row = right_row
                        right_row += 1
                    
                    # Nombre del botón
                    ttk.Label(table_frame, text=button_name).grid(row=current_row, column=col_offset, padx=5, pady=2, sticky=tk.W)
                    
                    # Frame para la entrada y el botón de borrado
                    entry_frame = ttk.Frame(table_frame)
                    entry_frame.grid(row=current_row, column=col_offset+1, padx=5, pady=2, sticky=tk.W)
                    
                    # Centrar el contenido del frame
                    entry_frame.columnconfigure(0, weight=1)
                    entry_frame.columnconfigure(1, weight=0)
                    
                    # Entrada para la tecla
                    current_key = current_mappings.get(button_name)
                    key_text = self._format_key(current_key)
                    
                    entry = ttk.Entry(entry_frame, width=20)
                    entry.insert(0, key_text)
                    entry.grid(row=0, column=0, padx=(0, 2), sticky=tk.W)
                    
                    # Botón para borrar la asignación
                    clear_button = ttk.Button(
                        entry_frame, 
                        text="×", 
                        width=2,
                        command=lambda e=entry: self.clear_key(e)
                    )
                    clear_button.grid(row=0, column=1)
                    
                    # Guardar referencia a la entrada
                    self.key_entries[button_name] = entry
                    
                    # Bind para capturar teclas
                    entry.bind('<Key>', lambda e, btn=button_name: self.on_key_press(e, btn))
                    entry.bind('<FocusOut>', lambda e, btn=button_name: self.on_focus_out(e, btn))
                    
                    button_count += 1
        
        # Frame para los botones de acción (fuera del canvas scrollable)
        button_frame = ttk.Frame(self.window)
        button_frame.grid(row=1, column=0, pady=10, sticky=(tk.W, tk.E))
        
        # Centrar los botones
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)
        button_frame.columnconfigure(3, weight=1)
        
        ttk.Button(
            button_frame,
            text="Cancelar",
            command=self.window.destroy
        ).grid(row=0, column=0, padx=5)
        
        ttk.Button(
            button_frame,
            text="Guardar",
            command=self.save_all_keys
        ).grid(row=0, column=1, padx=5)
        
        ttk.Button(
            button_frame,
            text="Restaurar Valores por Defecto",
            command=self.restore_defaults
        ).grid(row=0, column=2, padx=5)
        
        # Configurar el grid para que se expanda
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Colocar el canvas y scrollbar
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configurar el canvas para que se expanda con la ventana
        def on_configure(event):
            canvas.itemconfig(canvas.find_withtag("all")[0], width=event.width)
        
        canvas.bind('<Configure>', on_configure)
        
        # Ajustar el tamaño de la ventana al contenido
        self.window.update_idletasks()
        
        # Calcular el tamaño necesario para mostrar todo el contenido
        # Ancho: suficiente para las dos columnas de botones + márgenes
        width = max(800, table_frame.winfo_reqwidth() + 50)
        
        # Alto: suficiente para mostrar la mayoría del contenido + espacio para scroll
        height = min(600, max(400, table_frame.winfo_reqheight() + 150))
        
        # Centrar la ventana
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
        
        # Hacer la ventana redimensionable
        self.window.resizable(True, True)
    
    def _format_key(self, key):
        if key is None:
            return "Ninguna"
        if isinstance(key, Key):
            return key.name
        if isinstance(key, KeyCode):
            return key.char
        return str(key)
    
    def on_key_press(self, event, button_name):
        # Prevenir que la tecla se escriba en la entrada
        event.widget.delete(0, tk.END)
        
        if event.keysym == 'Escape':
            event.widget.master.focus_set()
            return "break"
        
        # Manejo especial para la tecla Return (Intro)
        if event.keysym == 'Return':
            try:
                # Intentar primero con 'enter'
                key = Key.enter
            except AttributeError:
                try:
                    # Si no funciona, intentar con 'return'
                    key = Key.return_
                except AttributeError:
                    # Si ninguno funciona, usar un enfoque alternativo
                    print("No se pudo encontrar la tecla Enter/Return en la clase Key")
                    return "break"
            
            event.widget.insert(0, self._format_key(key))
            # Mover el foco al siguiente campo
            next_widget = event.widget.tk_focusNext()
            if next_widget:
                next_widget.focus_set()
            return "break"
        
        # Manejar otras teclas especiales
        special_keys = {
            'Tab': 'tab',
            'BackSpace': 'backspace',
            'Delete': 'delete',
            'Space': 'space',
            'Home': 'home',
            'End': 'end',
            'Page_Up': 'page_up',
            'Page_Down': 'page_down',
            'Insert': 'insert',
            'F1': 'f1', 'F2': 'f2', 'F3': 'f3', 'F4': 'f4', 'F5': 'f5',
            'F6': 'f6', 'F7': 'f7', 'F8': 'f8', 'F9': 'f9', 'F10': 'f10',
            'F11': 'f11', 'F12': 'f12'
        }
        
        if event.keysym in special_keys:
            try:
                key_name = special_keys[event.keysym]
                key = getattr(Key, key_name)
                event.widget.insert(0, self._format_key(key))
                # Mover el foco al siguiente campo
                next_widget = event.widget.tk_focusNext()
                if next_widget:
                    next_widget.focus_set()
                return "break"
            except AttributeError:
                pass
        
        # Ignorar teclas modificadoras solas
        if event.keysym in ['Shift_L', 'Shift_R', 'Control_L', 'Control_R', 'Alt_L', 'Alt_R']:
            return "break"
        
        if len(event.keysym) == 1:
            key = KeyCode.from_char(event.char)
        else:
            try:
                key = getattr(Key, event.keysym.lower())
            except AttributeError:
                return "break"
        
        # Actualizar la entrada con la nueva tecla
        event.widget.insert(0, self._format_key(key))
        
        # Mover el foco al siguiente campo
        next_widget = event.widget.tk_focusNext()
        if next_widget:
            next_widget.focus_set()
        
        return "break"
    
    def on_focus_out(self, event, button_name):
        # Si el campo está vacío, mostrar "Ninguna"
        if not event.widget.get():
            event.widget.insert(0, "Ninguna")
    
    def save_all_keys(self):
        # Guardar todas las asignaciones
        for button_name, entry in self.key_entries.items():
            key_text = entry.get()
            
            # Convertir el texto a un objeto Key o KeyCode
            if key_text == "Ninguna":
                update_key_mapping(button_name, None)
            else:
                # Intentar encontrar la tecla en Key
                try:
                    key = getattr(Key, key_text.lower())
                    update_key_mapping(button_name, key)
                except AttributeError:
                    # Si no es una tecla especial, asumir que es un carácter
                    if len(key_text) == 1:
                        key = KeyCode.from_char(key_text)
                        update_key_mapping(button_name, key)
        
        messagebox.showinfo("Configuración Guardada", "Las asignaciones de teclas han sido guardadas correctamente.")
        self.window.destroy()
    
    def restore_defaults(self):
        # Restaurar las teclas por defecto
        default_keys = {
            'Up': Key.up,
            'Down': Key.down,
            'Left': Key.left,
            'Right': Key.right,
            'A': KeyCode.from_char('a'),
            'B': KeyCode.from_char('b'),
            'X': KeyCode.from_char('x'),
            'Y': KeyCode.from_char('y'),
            'Left brake': KeyCode.from_char('q'),
            'Right brake': KeyCode.from_char('w'),
            'Left shift 1': KeyCode.from_char('e'),
            'Left shift 2': KeyCode.from_char('r'),
            'Right shift 1': KeyCode.from_char('t'),
            'Right shift 2': KeyCode.from_char('y'),
            'Square': KeyCode.from_char('s'),
            'Circle': KeyCode.from_char('c'),
            'Triangle': KeyCode.from_char('t'),
            'Z': KeyCode.from_char('z'),
            'Left Campagnolo': KeyCode.from_char('l'),
            'Right Campagnolo': KeyCode.from_char('r')
        }
        
        # Actualizar todas las entradas con las teclas por defecto
        for button_name, key in default_keys.items():
            if button_name in self.key_entries:
                self.key_entries[button_name].delete(0, tk.END)
                self.key_entries[button_name].insert(0, self._format_key(key))
        
        # Mostrar mensaje informativo
        messagebox.showinfo(
            "Valores Restaurados",
            "Los valores por defecto han sido restaurados.\n\n" +
            "Puedes revisar los cambios y:\n" +
            "- Hacer clic en 'Guardar' para aplicar los cambios\n" +
            "- Hacer clic en 'Cancelar' para descartar los cambios"
        )

    def clear_key(self, entry):
        """Borra la asignación de tecla y deja el campo en blanco"""
        entry.delete(0, tk.END)
        entry.insert(0, "Ninguna")
        
        # Mover el foco al siguiente campo
        next_widget = entry.tk_focusNext()
        if next_widget:
            next_widget.focus_set()

class SquareUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Control Square")
        
        # Aplicar colores a la ventana principal
        self.root.configure(bg=COLORS["bg"])
        
        # Cola para comunicación entre el hilo BLE y la UI
        self.message_queue = queue.Queue()
        
        # Configurar la cola en el controlador
        set_message_queue(self.message_queue)
        
        # Frame principal
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Barra de herramientas
        toolbar_frame = ttk.Frame(main_frame)
        toolbar_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Botón de configuración global
        config_button = ttk.Button(
            toolbar_frame,
            text="Configurar Teclas",
            command=self.open_global_config
        )
        config_button.grid(row=0, column=0, padx=5)
        
        # Estado de conexión
        self.connection_frame = ttk.LabelFrame(main_frame, text="Estado de Conexión", padding="5")
        self.connection_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.connection_status = ttk.Label(self.connection_frame, text="Desconectado", foreground="red")
        self.connection_status.grid(row=0, column=0, padx=5, pady=5)
        
        # Frame para los botones
        self.buttons_frame = ttk.LabelFrame(main_frame, text="Control Square", padding="10")
        self.buttons_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Crear etiquetas para cada botón
        self.button_labels = {}
        self.button_frames = {}
        
        # Encontrar el nombre de botón más largo para establecer un ancho fijo
        max_button_name_length = max(len(name) for name in BUTTON_MAPPING.values())
        button_width = max_button_name_length + 2  # Añadir un poco de espacio extra
        
        # Organizar los botones por categorías
        row = 0
        for category, buttons in BUTTON_CATEGORIES.items():
            # Frame para la categoría
            category_frame = ttk.Frame(self.buttons_frame)
            category_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
            
            # Etiqueta de categoría
            category_label = ttk.Label(
                category_frame, 
                text=category,
                font=("Arial", 10, "bold")
            )
            category_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
            
            # Frame para los botones de esta categoría
            buttons_container = ttk.Frame(category_frame)
            buttons_container.grid(row=1, column=0, sticky=(tk.W, tk.E))
            
            # Botones de esta categoría
            col = 0
            for button_name in buttons:
                if button_name in BUTTON_MAPPING.values():
                    # Crear un frame para cada botón con borde y padding
                    frame = ttk.Frame(buttons_container, style='Button.TFrame')
                    frame.grid(row=0, column=col, padx=5, pady=5, sticky=(tk.W, tk.E))
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
                    
                    self.button_labels[button_name] = status
                    
                    # Avanzar a la siguiente posición
                    col += 1
            
            # Añadir una fila extra después de cada categoría
            row += 1
        
        # Log de eventos
        self.log_frame = ttk.LabelFrame(main_frame, text="Registro de Eventos", padding="5")
        self.log_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.log_text = tk.Text(
            self.log_frame, 
            height=10, 
            width=80,
            bg=COLORS["log_bg"],
            fg=COLORS["log_fg"]
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar para el log
        scrollbar = ttk.Scrollbar(self.log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.log_text['yscrollcommand'] = scrollbar.set
        
        # Configurar el grid para que se expanda
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
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
    
    def open_global_config(self):
        GlobalConfigWindow(self.root)
    
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
                        foreground=COLORS["status_connected"] if "Connected" in status else COLORS["status_disconnected"]
                    )
                elif message.startswith("BUTTON:"):
                    button_name = message.split(":")[1]
                    if button_name in self.button_labels:
                        # Cambiar el color del botón a verde
                        self.button_labels[button_name].config(foreground=COLORS["button_pressed"])
                        # Programar el cambio de vuelta a gris después de 200ms
                        self.root.after(200, lambda btn=button_name: self.button_labels[btn].config(foreground=COLORS["button_normal"]))
                
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