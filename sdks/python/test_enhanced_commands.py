#!/usr/bin/env python3
"""
Test the enhanced hot command detection with user's actual phrases
"""

import sys
import os
sys.path.append('.')

from memory import detect_hot_command

# Test phrases from the user's transcript
test_phrases = [
    "Oh, me. Open notepad.",
    "Just open the notepad, please.",
    "Oh, me.",  # Should not trigger (no command)
    "Open notepad.",  # Should not trigger (no omi trigger)
    "Hey, army.",  # Should not trigger (no command)
    "Army. Open notepad.",  # Should trigger
    "O m I. Open notepad.",  # Should trigger
    "when I'm in a virtual environment",  # Should not trigger
]

print("🧪 Enhanced Hot Command Detection Test")
print("=" * 50)

for i, phrase in enumerate(test_phrases, 1):
    print(f"Test {i}: '{phrase}'")
    result = detect_hot_command(phrase)
    status = "✅ TRIGGERED" if result else "❌ No match"
    print(f"   → {status}")
    if result:
        print(f"   → Result: {result}")
    print()
