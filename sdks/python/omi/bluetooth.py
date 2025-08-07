import asyncio
from bleak import BleakScanner, BleakClient

def print_devices():
    devices = asyncio.run(BleakScanner.discover())
    for i, d in enumerate(devices):
        print(f"{i}. {d.name} [{d.address}]")

async def listen_to_omi(mac_address, char_uuid, data_handler, status_callback=None):
    try:
        async with BleakClient(mac_address) as client:
            print(f"Connected to {mac_address}")
            if status_callback:
                status_callback(f"✅ Connected to Omi device ({mac_address})")
            await client.start_notify(char_uuid, data_handler)
            print("Listening for data...")
            if status_callback:
                status_callback("🎧 Listening for audio data...")
            await asyncio.sleep(99999)
    except Exception as e:
        print(f"❌ Bluetooth connection error: {e}")
        if status_callback:
            status_callback(f"❌ Bluetooth error: {e}")
        raise
