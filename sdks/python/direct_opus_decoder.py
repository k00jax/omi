#!/usr/bin/env python3
"""
Direct ctypes-based Opus decoder
This bypasses opuslib issues by calling opus functions directly
"""

import ctypes
import os
from ctypes import c_int, c_void_p, c_char_p, c_short, POINTER, byref

class DirectOpusDecoder:
    """Direct Opus decoder using ctypes - bypasses opuslib dependency issues"""
    
    OPUS_OK = 0
    OPUS_APPLICATION_VOIP = 2048
    
    def __init__(self, sample_rate=16000, channels=1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.decoder = None
        self.lib = None
        self.functional = False
        
        # Try to load the Opus library
        dll_names = ["opus.dll", "libopus-0.dll"]
        for dll_name in dll_names:
            if os.path.exists(dll_name):
                try:
                    self.lib = ctypes.CDLL(dll_name)
                    print(f"✅ Loaded Opus library: {dll_name}")
                    break
                except Exception as e:
                    print(f"⚠️  Could not load {dll_name}: {e}")
        
        if self.lib is None:
            print("❌ Could not load any Opus library")
            return
        
        # Define Opus function signatures
        try:
            # opus_decoder_create(Fs, channels, error)
            self.lib.opus_decoder_create.argtypes = [c_int, c_int, POINTER(c_int)]
            self.lib.opus_decoder_create.restype = c_void_p
            
            # opus_decode(decoder, data, len, pcm, frame_size, decode_fec)
            self.lib.opus_decode.argtypes = [c_void_p, c_char_p, c_int, POINTER(c_short), c_int, c_int]
            self.lib.opus_decode.restype = c_int
            
            # opus_decoder_destroy(decoder)
            self.lib.opus_decoder_destroy.argtypes = [c_void_p]
            self.lib.opus_decoder_destroy.restype = None
            
            # Create the decoder
            error = c_int()
            self.decoder = self.lib.opus_decoder_create(sample_rate, channels, byref(error))
            
            if error.value == self.OPUS_OK and self.decoder:
                self.functional = True
                print("✅ Direct Opus decoder created successfully!")
            else:
                print(f"❌ Failed to create Opus decoder, error: {error.value}")
                
        except Exception as e:
            print(f"❌ Error setting up Opus functions: {e}")
    
    def decode(self, opus_data, frame_size=960):
        """Decode Opus data to 16-bit PCM"""
        if not self.functional or not self.decoder:
            return None
            
        try:
            # Create output buffer for PCM samples
            pcm_buffer = (c_short * frame_size)()
            
            # Decode the Opus frame
            samples_decoded = self.lib.opus_decode(
                self.decoder,
                opus_data,
                len(opus_data),
                pcm_buffer,
                frame_size,
                0  # decode_fec = False
            )
            
            if samples_decoded > 0:
                # Convert C short array to bytes (16-bit little-endian PCM)
                result = bytearray()
                for i in range(samples_decoded):
                    sample = pcm_buffer[i]
                    # Little-endian 16-bit
                    result.append(sample & 0xFF)
                    result.append((sample >> 8) & 0xFF)
                return bytes(result)
            else:
                if samples_decoded < 0:
                    print(f"Opus decode error: {samples_decoded}")
                return None
                
        except Exception as e:
            print(f"Exception in decode: {e}")
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
        return True
    else:
        print("❌ Direct decoder failed to initialize")
        return False


if __name__ == "__main__":
    success = test_direct_decoder()
    if success:
        print("\n🎉 Direct Opus decoder is ready!")
        print("This can be used as a replacement for opuslib in the main decoder.")
    else:
        print("\n❌ Direct decoder test failed.")
        print("The DLL may be missing dependencies or have compatibility issues.")
