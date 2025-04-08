import asyncio
from bleak import BleakClient, BleakScanner
import time

# Constants
DEVICE_NAME = "SQUARE"
CHARACTERISTIC_UUID = "347b0043-7635-408b-8918-8ff3949ce592"
RECONNECT_DELAY = 5  # seconds between reconnection attempts

# Button mapping
BUTTON_MAPPING = {
    "0201610000020002020c321e0101": "Up",
    "0201610000010002020c321e0101": "Left",
    "0201610000080002020c321e0101": "Down",
    "0201610000040002020c321e0101": "Right",
    "0201610000200002020c321e0101": "X",
    "0201610000100002020c321e0101": "Square",
    "0201610000800002020c321e0101": "Left Campagnolo",
    "0201610000400002020c321e0101": "Left brake",
    "0201610000000202020c321e0101": "Left shift 1",
    "0201610000000102020c321e0101": "Left shift 2",
    "0201610200000002020c321e0101": "Y",
    "0201610100000002020c321e0101": "A",
    "0201610800000002020c321e0101": "B",
    "0201610400000002020c321e0101": "Z",
    "0201612000000002020c321e0101": "Circle",
    "0201611000000002020c321e0101": "Triangle",
    "0201618000000002020c321e0101": "Right Campagnolo",
    "0201614000000002020c321e0101": "Right brake",
    "0201610002000002020c321e0101": "Right shift 1",
    "0201610001000002020c321e0101": "Right shift 2"
}

# Variable to store the last value
last_value = None

def notification_handler(sender, data):
    """Handler for notifications received from the BLE device"""
    global last_value
    current_value = data.hex()
    if current_value != last_value:
        # If the value is in our mapping, it's a button press
        # Otherwise, consider it as "No button pressed"
        button_name = BUTTON_MAPPING.get(current_value, "No button pressed")
        print(f"Button pressed: {button_name} (hex: {current_value})")
        last_value = current_value

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