import asyncio
from bleak import BleakClient, BleakScanner
import time
from pynput.keyboard import Key, Controller, KeyCode

# Constants
DEVICE_NAME = "SQUARE"
CHARACTERISTIC_UUID = "347b0043-7635-408b-8918-8ff3949ce592"
RECONNECT_DELAY = 5  # seconds between reconnection attempts

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

# Key mapping for button presses
KEY_MAPPING = {
    "Up": Key.up,
    "Left": Key.left,
    "Down": Key.down,
    "Right": Key.right,
    "X": None, # left steering
    "Square": KeyCode.from_char('r'), # pairing screen, 
    "Left Campagnolo": Key.left,
    "Left brake": None, # Toggles backward/forward view ('6'/'1')
    "Left shift 1": None,
    "Left shift 2": None,
    "Y": KeyCode.from_char('g'), # alternate power and watts and FC 
    "A": Key.enter,
    "B": Key.esc,
    "Z": KeyCode.from_char('t'), # garage screen
    "Circle": None, # Right steering
    "Triangle": Key.space, # Activate powerup
    "Right Campagnolo": Key.right,
    "Right brake": None,
    "Right shift 1": None,
    "Right shift 2": None
}

# Variable to store the last value
last_value = None
keyboard = Controller()
left_brake_is_forward_view = False

def extract_button_code(hex_value):
    """Extract the relevant part of the hex value that identifies the button"""
    # Simplified approach: use a fixed position in the hex value
    # Skip the first 6 characters (timestamp) and take the next 8 characters
    
    if len(hex_value) >= 14:  # Ensure we have enough characters
        # Extract 8 characters starting from position 6 (after timestamp)
        button_code = hex_value[6:14]
        
        # Check if this code is in our mapping
        if button_code in BUTTON_MAPPING:
            return button_code
    
    # If we can't identify a specific pattern, return the whole value
    return hex_value

def notification_handler(sender, data):
    """Handler for notifications received from the BLE device"""
    global last_value, left_brake_is_forward_view
    full_value = data.hex()
    
    # Extract the relevant part of the value that identifies the button
    current_value = extract_button_code(full_value)
    
    # Only compare the relevant part, ignoring the first 6 and last 13 digits
    if len(full_value) >= 19:  # Ensure we have enough characters
        current_relevant_part = full_value[6:-13]  # Ignore first 6 and last 13
        last_relevant_part = last_value[6:-13] if last_value else None
    else:
        current_relevant_part = full_value[6:]  # If not enough characters, only ignore first 6
        last_relevant_part = last_value[6:] if last_value else None
    
    if current_relevant_part != last_relevant_part:
        # If the value is in our mapping, it's a button press
        # Otherwise, consider it as "No button pressed"
        button_name = BUTTON_MAPPING.get(current_value, "No button pressed")
        if button_name == "No button pressed":
            # Simplified log message for unpressed button
            print("Unpressed button")
        else:
            print(f"Button pressed: {button_name} (full hex: {full_value}, button code: {current_value})")
        
        # Simulate key press if it's a valid button
        if button_name == "Left brake":
            left_brake_is_forward_view = not left_brake_is_forward_view
            if left_brake_is_forward_view:
                key = KeyCode.from_char('1')
                print(f"Simulating key press: {key} (Left brake - forward view)")
            else:
                key = KeyCode.from_char('6')
                print(f"Simulating key press: {key} (Left brake - backward view)")
            keyboard.press(key)
            keyboard.release(key)
        elif button_name != "No button pressed":
            key = KEY_MAPPING.get(button_name)
            if key:
                print(f"Simulating key press: {key}")
                keyboard.press(key)
                keyboard.release(key)
        
        last_value = full_value

async def connect_and_listen():
    """Function to connect to the device and listen for notifications"""
    while True:
        try:
            # Search and connect to the device
            print(f"Searching for device {DEVICE_NAME}...")
            device = await BleakScanner.find_device_by_name(DEVICE_NAME)
            
            if not device:
                print(f"Device {DEVICE_NAME} not found. Retrying in {RECONNECT_DELAY} seconds...")
                await asyncio.sleep(RECONNECT_DELAY)
                continue
                
            print(f"Device found, connecting...")
            
            async with BleakClient(device, timeout=10.0) as client:
                print(f"Connected to {device.name}")
                
                # Subscribe to notifications
                await client.start_notify(CHARACTERISTIC_UUID, notification_handler)
                print("Waiting for data...")
                
                # Keep connection until device disconnects
                while True:
                    if not client.is_connected:
                        print("Device disconnected")
                        break
                    await asyncio.sleep(1)
                    
        except Exception as e:
            print(f"Error: {str(e)}")
            print(f"Retrying connection in {RECONNECT_DELAY} seconds...")
            await asyncio.sleep(RECONNECT_DELAY)

async def main():
    await connect_and_listen()

if __name__ == "__main__":
    asyncio.run(main()) 