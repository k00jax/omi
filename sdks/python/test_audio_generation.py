#!/usr/bin/env python3
"""
Test script to validate the audio generation from our fallback decoder
"""

import os
import wave
from omi.decoder import OmiOpusDecoder

def test_audio_generation():
    """Test the fallback decoder and save some audio samples"""
    print("🧪 Testing fallback audio decoder...")
    
    decoder = OmiOpusDecoder()
    
    # Create some dummy Opus packet data (simulating what comes from Omi)
    test_packets = [
        # Simulated Opus packets with header + data
        b'\x00\x01\x02' + b'\x45\x67\x89\xab' * 20,  # Dummy packet 1
        b'\x00\x01\x02' + b'\x23\x45\x67\x89' * 25,  # Dummy packet 2  
        b'\x00\x01\x02' + b'\x78\x9a\xbc\xde' * 15,  # Dummy packet 3
    ]
    
    print(f"Decoder functional: {decoder.functional}")
    print(f"Using fallback: {not decoder.functional}")
    
    # Decode the packets and collect audio
    all_audio = bytearray()
    
    for i, packet in enumerate(test_packets):
        print(f"\n📦 Processing packet {i+1}:")
        print(f"   Input size: {len(packet)} bytes")
        
        decoded = decoder.decode_packet(packet)
        if decoded:
            print(f"   Decoded size: {len(decoded)} bytes")
            non_zero = sum(1 for b in decoded if b != 0)
            print(f"   Non-zero bytes: {non_zero}/{len(decoded)} ({100*non_zero/len(decoded):.1f}%)")
            all_audio.extend(decoded)
        else:
            print("   No audio decoded")
    
    # Save the generated audio to a WAV file for inspection
    if all_audio:
        output_file = "test_fallback_audio.wav"
        print(f"\n💾 Saving audio to {output_file}...")
        
        try:
            with wave.open(output_file, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(16000)  # 16kHz
                wav_file.writeframes(bytes(all_audio))
            
            print(f"✅ Audio saved! File size: {len(all_audio)} bytes")
            print(f"   Duration: {len(all_audio) / (16000 * 2):.2f} seconds")
            print(f"   You can play this file to hear what Deepgram receives")
            
        except Exception as e:
            print(f"❌ Failed to save audio: {e}")
    
    print("\n📊 Analysis:")
    if decoder.functional:
        print("✅ Using proper Opus decoder - audio should be high quality")
    else:
        print("⚠️  Using fallback decoder - audio is artificially generated")
        print("   This explains why Deepgram doesn't recognize it as speech")
        print("   The patterns look like audio data but lack speech characteristics")


if __name__ == "__main__":
    test_audio_generation()
