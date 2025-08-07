import asyncio
import os
import ctypes
import sys
from omi.bluetooth import listen_to_omi
from omi.transcribe import transcribe
from omi.decoder import OmiOpusDecoder
from asyncio import Queue
from memory import init_memory_storage, process_transcript_for_memory, cleanup_memory_storage
from env_config import setup_environment

OMI_MAC = "8680354F-04B6-6281-8CA4-D987E07D1065"
OMI_CHAR_UUID = "19B10001-E8F2-537E-4F6C-D104768A1214"

# Force-load libopus from local directory
dll_path = os.path.join(os.path.dirname(__file__), "libopus-0.dll")
if os.path.exists(dll_path):
    ctypes.cdll.LoadLibrary(dll_path)
else:
    print(f"❌ libopus-0.dll not found at: {dll_path}")
    sys.exit(1)

def main():
    # Setup environment variables
    print("🔧 Setting up environment...")
    if not setup_environment():
        print("❌ Environment setup failed. Check your configuration.")
        return
    
    api_key = os.getenv("DEEPGRAM_API_KEY")
    if not api_key:
        print("❌ DEEPGRAM_API_KEY is required but not set.")
        print("💡 Create a .env file based on .env.example")
        return

    # Initialize memory storage
    omi_api_key = os.getenv("OMI_API_KEY")
    if omi_api_key:
        print("🧠 Initializing memory storage with MCP...")
        init_memory_storage(omi_api_key, user_id=os.getenv("OMI_USER_ID", "default_user"))
    else:
        print("⚠️  OMI_API_KEY not set. Memory storage will use local fallback only.")
        init_memory_storage("dummy_key", user_id="default_user")  # Will fallback to local storage

    audio_queue = Queue()
    decoder = OmiOpusDecoder()

    def handle_ble_data(sender, data):
        decoded_pcm = decoder.decode_packet(data)
        if decoded_pcm:
            try:
                audio_queue.put_nowait(decoded_pcm)
            except Exception as e:
                print("Queue Error:", e)

    async def on_transcript(transcript):
        print("🎯 Caught transcript in handler:", transcript)

        # Process transcript for hot phrases and create memory
        memory_created = await process_transcript_for_memory(transcript)
        
        if memory_created:
            print("📌 Memory created successfully!")
        
        # Legacy trigger phrase detection (now handled by process_transcript_for_memory)
        # Keeping for backward compatibility
        if "note this" in transcript.lower():
            print("📌 Legacy trigger phrase detected!")

    async def run():
        try:
            await asyncio.gather(
                listen_to_omi(OMI_MAC, OMI_CHAR_UUID, handle_ble_data),
                transcribe(audio_queue, api_key, on_transcript)
            )
        finally:
            # Cleanup resources
            print("🧹 Cleaning up...")
            await cleanup_memory_storage()

    asyncio.run(run())

if __name__ == '__main__':
    main()
