import os
import asyncio
from bleak import BleakClient, BleakScanner
from dotenv import load_dotenv

load_dotenv()
OMI_MAC = os.getenv("OMI_MAC")

if not OMI_MAC:
    print("❌ OMI_MAC not found in .env file. Please set it before running.")
    exit(1)

async def main():
    print(f"🔍 Scanning for Omi device at {OMI_MAC}...")
    devices = await BleakScanner.discover(timeout=5.0)

    matched_device = next((d for d in devices if d.address.lower() == OMI_MAC.lower()), None)
    if not matched_device:
        print(f"❌ Device with MAC {OMI_MAC} not found in BLE scan.")
        return

    print(f"✅ Found: {matched_device.name} [{matched_device.address}] — Connecting...")

    async with BleakClient(OMI_MAC) as client:
        print(f"🔗 Connected to {OMI_MAC}")
        services = await client.get_services()
        for service in services:
            print(f"Service UUID: {service.uuid}")
            for char in service.characteristics:
                print(f"  ↳ Characteristic UUID: {char.uuid}")
                print(f"     Properties: {char.properties}")

asyncio.run(main())
