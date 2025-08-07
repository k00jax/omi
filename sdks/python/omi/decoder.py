import os
import ctypes
import sys

# Try to pre-load libopus-0.dll on Windows
if os.name == 'nt':  # Windows
    dll_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "libopus-0.dll")
    if os.path.exists(dll_path):
        try:
            ctypes.cdll.LoadLibrary(os.path.abspath(dll_path))
        except Exception as e:
            print(f"⚠️  Warning: Could not pre-load libopus-0.dll: {e}")

# Try to import opuslib, with fallback handling
try:
    from opuslib import Decoder
    OPUSLIB_AVAILABLE = True
except Exception as e:
    print(f"⚠️  opuslib not available: {e}")
    print("🔄 Using fallback decoder (limited functionality)")
    OPUSLIB_AVAILABLE = False
    
    # Import fallback decoder
    try:
        # Create a simple fallback decoder class directly
        class Decoder:
            def __init__(self, sample_rate, channels):
                self.sample_rate = sample_rate
                self.channels = channels
                print("⚠️  Using minimal fallback decoder")
            
            def decode(self, data, frame_size=None, decode_fec=False):
                # Return silent PCM data for the expected frame size
                if frame_size:
                    return b'\x00' * (frame_size * 2)  # 2 bytes per sample for 16-bit
                return b'\x00' * 1920  # Default frame size * 2
    except Exception:
        # Final fallback
        class Decoder:
            def __init__(self, sample_rate, channels):
                self.sample_rate = sample_rate
                self.channels = channels
            
            def decode(self, data, frame_size=None, decode_fec=False):
                return b''

class OmiOpusDecoder:
    def __init__(self):
        try:
            self.decoder = Decoder(16000, 1)  # 16kHz mono
            self.functional = OPUSLIB_AVAILABLE
            if OPUSLIB_AVAILABLE:
                print("✅ Opus decoder initialized successfully")
            else:
                print("⚠️  Using fallback decoder - audio decoding will be limited")
        except Exception as e:
            print(f"❌ Decoder initialization failed: {e}")
            # Create a dummy decoder
            self.decoder = Decoder(16000, 1)
            self.functional = False

    def decode_packet(self, data):
        if len(data) <= 3:
            return b''

        # Remove 3-byte header
        clean_data = bytes(data[3:])

        # Decode Opus to PCM 16-bit
        try:
            if self.functional:
                pcm = self.decoder.decode(clean_data, 960, decode_fec=False)
                return pcm
            else:
                # Fallback: return silent audio or placeholder
                print("🔇 Fallback decoder: returning silence")
                return b'\x00' * 1920  # 960 samples * 2 bytes per sample
        except Exception as e:
            print("Opus decode error:", e)
            return b''
