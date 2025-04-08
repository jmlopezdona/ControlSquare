import asyncio
from bleak import BleakClient, BleakScanner
import time

# Constants
DEVICE_NAME = "SQUARE"
CHARACTERISTIC_UUID = "347b0043-7635-408b-8918-8ff3949ce592"
RECONNECT_DELAY = 5  # seconds between reconnection attempts

# Variable to store the last value
last_value = None

def notification_handler(sender, data):
    """Handler for notifications received from the BLE device"""
    global last_value
    current_value = data.hex()
    if current_value != last_value:
        print(f"Value: {current_value}")
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