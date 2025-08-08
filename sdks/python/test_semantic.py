#!/usr/bin/env python3
"""
Test script for semantic intent matching
"""

import sys
from memory import detect_hot_command, SEMANTIC_MATCHING_AVAILABLE

print('🧠 Semantic Intent Matching Test')
print('=' * 40)
print(f'Semantic matching available: {SEMANTIC_MATCHING_AVAILABLE}')
print()

# Test cases
test_cases = [
    'hey omi open notepad',
    'omi, can you please open notepad for me?',
    'hey omi launch notepad now',
    'just open notepad',  # Should fail - no trigger
    'hey omi start up notepad',
    'omi open notes app',
]

for i, test_phrase in enumerate(test_cases, 1):
    print(f'Test {i}: "{test_phrase}"')
    result = detect_hot_command(test_phrase)
    print(f'   Result: {result}')
    print()
