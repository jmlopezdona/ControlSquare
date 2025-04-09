import asyncio
from bleak import BleakClient, BleakScanner
import time
from pynput.keyboard import Key, Controller, KeyCode
import queue
import json
import os

# Constants
DEVICE_NAME = "SQUARE"
CHARACTERISTIC_UUID = "347b0043-7635-408b-8918-8ff3949ce592"
RECONNECT_DELAY = 5  # seconds between reconnection attempts
CONFIG_FILE = "key_mapping.json"

# Cola global para mensajes
message_queue = None

# Button mapping (all codes have the same length - 8 characters)
BUTTON_MAPPING = {
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
}

# Default key mapping
DEFAULT_KEY_MAPPING = {
    "Up": Key.up,
    "Left": Key.left,
    "Down": Key.down,
    "Right": Key.right,
    "X": None,
    "Square": KeyCode.from_char('r'),
    "Left Campagnolo": Key.left,
    "Left brake": KeyCode.from_char('6'),
    "Left shift 1": None,
    "Left shift 2": None,
    "Y": KeyCode.from_char('g'),
    "A": Key.enter,
    "B": Key.esc,
    "Z": KeyCode.from_char('t'),
    "Circle": None,
    "Triangle": Key.space,
    "Right Campagnolo": Key.right,
    "Right brake": KeyCode.from_char('1'),
    "Right shift 1": None,
    "Right shift 2": None
}

# Variable to store the last value
last_value = None
keyboard = Controller()
key_mapping = {}

def load_key_mapping():
    """Load key mapping from file or use default"""
    global key_mapping
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                saved_mapping = json.load(f)
                # Convert string keys back to Key objects
                key_mapping = {}
                for button, key_str in saved_mapping.items():
                    if key_str.startswith('Key.'):
                        key_name = key_str.split('.')[1]
                        key_mapping[button] = getattr(Key, key_name)
                    elif key_str.startswith('KeyCode.from_char'):
                        char = key_str.split("'")[1]
                        key_mapping[button] = KeyCode.from_char(char)
                    else:
                        key_mapping[button] = None
        except Exception as e:
            print(f"Error loading key mapping: {e}")
            key_mapping = DEFAULT_KEY_MAPPING.copy()
    else:
        key_mapping = DEFAULT_KEY_MAPPING.copy()

def save_key_mapping():
    """Save current key mapping to file"""
    # Convert Key objects to strings for JSON serialization
    serializable_mapping = {}
    for button, key in key_mapping.items():
        if isinstance(key, Key):
            serializable_mapping[button] = f"Key.{key.name}"
        elif isinstance(key, KeyCode):
            serializable_mapping[button] = f"KeyCode.from_char('{key.char}')"
        else:
            serializable_mapping[button] = None
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump(serializable_mapping, f, indent=4)

def set_message_queue(queue):
    """Set the global message queue for UI communication"""
    global message_queue
    message_queue = queue

def send_message(message):
    """Send a message to the UI through the queue"""
    if message_queue:
        message_queue.put(message)

def update_key_mapping(button_name, new_key):
    """Update the key mapping for a button"""
    global key_mapping
    key_mapping[button_name] = new_key
    save_key_mapping()
    send_message(f"Key mapping updated for {button_name}")

def get_key_mapping():
    """Get the current key mapping"""
    return key_mapping.copy()

def extract_button_code(hex_value):
    """Extract the relevant part of the hex value that identifies the button"""
    if len(hex_value) >= 14:
        button_code = hex_value[6:14]
        if button_code in BUTTON_MAPPING:
            return button_code
    return hex_value

def notification_handler(sender, data):
    """Handler for notifications received from the BLE device"""
    global last_value
    full_value = data.hex()
    
    current_value = extract_button_code(full_value)
    
    if len(full_value) >= 19:
        current_relevant_part = full_value[6:-13]
        last_relevant_part = last_value[6:-13] if last_value else None
    else:
        current_relevant_part = full_value[6:]
        last_relevant_part = last_value[6:] if last_value else None
    
    if current_relevant_part != last_relevant_part:
        button_name = BUTTON_MAPPING.get(current_value, "No button pressed")
        if button_name == "No button pressed":
            send_message("Unpressed button")
        else:
            message = f"Button pressed: {button_name} (full hex: {full_value}, button code: {current_value})"
            send_message(message)
            send_message(f"BUTTON:{button_name}")
        
        if button_name != "No button pressed":
            key = key_mapping.get(button_name)
            if key:
                send_message(f"Simulating key press: {key}")
                keyboard.press(key)
                keyboard.release(key)
        
        last_value = full_value

# Load key mapping at startup
load_key_mapping()

async def connect_and_listen():
    """Function to connect to the device and listen for notifications"""
    while True:
        try:
            # Search and connect to the device
            send_message(f"Searching for device {DEVICE_NAME}...")
            device = await BleakScanner.find_device_by_name(DEVICE_NAME)
            
            if not device:
                send_message(f"Device {DEVICE_NAME} not found. Retrying in {RECONNECT_DELAY} seconds...")
                await asyncio.sleep(RECONNECT_DELAY)
                continue
                
            send_message(f"Device found, connecting...")
            
            async with BleakClient(device, timeout=10.0) as client:
                send_message(f"Connected to {device.name}")
                send_message("CONNECTION:Connected")
                
                # Subscribe to notifications
                await client.start_notify(CHARACTERISTIC_UUID, notification_handler)
                send_message("Waiting for data...")
                
                # Keep connection until device disconnects
                while True:
                    if not client.is_connected:
                        send_message("Device disconnected")
                        send_message("CONNECTION:Disconnected")
                        break
                    await asyncio.sleep(1)
                    
        except Exception as e:
            error_message = f"Error: {str(e)}"
            send_message(error_message)
            send_message("CONNECTION:Error")
            send_message(f"Retrying connection in {RECONNECT_DELAY} seconds...")
            await asyncio.sleep(RECONNECT_DELAY)

async def main():
    await connect_and_listen()

if __name__ == "__main__":
    asyncio.run(main()) 