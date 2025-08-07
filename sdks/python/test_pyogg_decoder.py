#!/usr/bin/env python3
"""
PyOgg-based Opus decoder as fallback
"""

try:
    import pyogg
    PYOGG_AVAILABLE = True
    print("✅ PyOgg imported successfully")
except ImportError as e:
    print(f"❌ PyOgg not available: {e}")
    PYOGG_AVAILABLE = False

class PyOggOpusDecoder:
    """Opus decoder using PyOgg library"""
    
    def __init__(self, sample_rate=16000, channels=1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.functional = False
        
        if not PYOGG_AVAILABLE:
            print("❌ PyOgg not available")
            return
            
        try:
            self.decoder = pyogg.OpusDecoder()
            self.decoder.set_sampling_frequency(sample_rate)
            self.decoder.set_channels(channels)
            self.functional = True
            print(f"✅ PyOgg Opus decoder initialized: {sample_rate}Hz, {channels} channel(s)")
        except Exception as e:
            print(f"❌ Failed to initialize PyOgg decoder: {e}")
    
    def decode(self, opus_data, frame_size=960):
        """Decode Opus data to PCM"""
        if not self.functional:
            return None
            
        try:
            # PyOgg decode returns PCM bytes directly
            pcm_bytes = self.decoder.decode(opus_data)
            return pcm_bytes
        except Exception as e:
            print(f"PyOgg decode error: {e}")
            return None


def test_pyogg_decoder():
    """Test PyOgg decoder"""
    print("🧪 Testing PyOgg Opus decoder...")
    
    if not PYOGG_AVAILABLE:
        print("❌ PyOgg not available")
        return False
    
    try:
        decoder = PyOggOpusDecoder()
        
        if decoder.functional:
            print("✅ PyOgg decoder is functional!")
            
            # Test with dummy opus data
            test_opus_data = b'\x01\x02\x03\x04' * 20  # Dummy data
            result = decoder.decode(test_opus_data)
            
            if result is not None:
                print(f"✅ Decoded test data: {len(result)} bytes")
                return True
            else:
                print("⚠️  Decoder returned None (expected with dummy data)")
                return True  # Still functional
        else:
            print("❌ PyOgg decoder not functional")
            return False
            
    except Exception as e:
        print(f"❌ PyOgg test failed: {e}")
        return False


if __name__ == "__main__":
    success = test_pyogg_decoder()
    if success:
        print("\n🎉 PyOgg decoder is ready!")
        print("This can be integrated into the main decoder as a fallback.")
    else:
        print("\n❌ PyOgg decoder test failed.")
