#!/usr/bin/env python3
"""
Direct Opus decoder using ctypes - bypassing opuslib
"""

import ctypes
import os
from ctypes import c_int, c_void_p, c_char_p, c_short, POINTER, byref

class DirectOpusDecoder:
    """Direct Opus decoder using ctypes instead of opuslib"""
    
    def __init__(self):
        self.decoder = None
        self.functional = False
        
        # Try to load the Opus library directly
        dll_paths = [
            "libopus-0.dll",
            "opus.dll", 
            "libopus.dll"
        ]
        
        self.lib = None
        for dll_path in dll_paths:
            if os.path.exists(dll_path):
                try:
                    self.lib = ctypes.CDLL(dll_path)
                    print(f"✅ Loaded Opus library: {dll_path}")
                    break
                except Exception as e:
                    print(f"⚠️  Could not load {dll_path}: {e}")
        
        if self.lib is None:
            print("❌ Could not load any Opus library")
            return
        
        # Define the Opus functions we need
        try:
            # opus_decoder_create
            self.lib.opus_decoder_create.argtypes = [c_int, c_int, POINTER(c_int)]
            self.lib.opus_decoder_create.restype = c_void_p
            
            # opus_decode
            self.lib.opus_decode.argtypes = [c_void_p, c_char_p, c_int, POINTER(c_short), c_int, c_int]
            self.lib.opus_decode.restype = c_int
            
            # opus_decoder_destroy
            self.lib.opus_decoder_destroy.argtypes = [c_void_p]
            self.lib.opus_decoder_destroy.restype = None
            
            # Create decoder
            error = c_int()
            self.decoder = self.lib.opus_decoder_create(16000, 1, byref(error))
            
            if error.value == 0 and self.decoder:
                self.functional = True
                print("✅ Direct Opus decoder created successfully!")
            else:
                print(f"❌ Failed to create Opus decoder, error: {error.value}")
                
        except Exception as e:
            print(f"❌ Error setting up Opus functions: {e}")
    
    def decode(self, opus_data, frame_size=960):
        """Decode Opus data to PCM"""
        if not self.functional or not self.decoder:
            return None
            
        try:
            # Create output buffer
            pcm_buffer = (c_short * frame_size)()
            
            # Decode
            samples = self.lib.opus_decode(
                self.decoder,
                opus_data,
                len(opus_data),
                pcm_buffer,
                frame_size,
                0  # decode_fec
            )
            
            if samples > 0:
                # Convert to bytes
                result = bytearray()
                for i in range(samples):
                    sample = pcm_buffer[i]
                    result.append(sample & 0xFF)
                    result.append((sample >> 8) & 0xFF)
                return bytes(result)
            else:
                print(f"Opus decode returned {samples}")
                return None
                
        except Exception as e:
            print(f"Opus decode error: {e}")
            return None
    
    def __del__(self):
        """Clean up decoder"""
        if self.functional and self.decoder and self.lib:
            try:
                self.lib.opus_decoder_destroy(self.decoder)
            except:
                pass


def test_direct_decoder():
    """Test the direct Opus decoder"""
    print("🧪 Testing direct Opus decoder...")
    
    decoder = DirectOpusDecoder()
    
    if decoder.functional:
        print("✅ Direct decoder is functional!")
        
        # Test with some dummy data
        test_data = b'\x45\x67\x89\xab' * 10
        result = decoder.decode(test_data)
        
        if result:
            print(f"✅ Decoded {len(test_data)} bytes to {len(result)} bytes")
            non_zero = sum(1 for b in result if b != 0)
            print(f"   Non-zero bytes: {non_zero}/{len(result)}")
        else:
            print("❌ Decoding failed")
    else:
        print("❌ Direct decoder not functional")


if __name__ == "__main__":
    test_direct_decoder()
