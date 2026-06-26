#!/usr/bin/env python3
"""Generate all audio files for the Ghost Chase game"""
import os
import sys

# Navigate to script directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("🎵 Ghost Chase - Audio Generation")
print("=" * 50)

try:
    # Import and run the sound creation script
    exec(open('create_sounds.py').read())
    
    print("\n" + "=" * 50)
    print("✓ All audio files generated successfully!")
    print("\nGenerated files:")
    print("  • start_button.wav - Start button sound")
    print("  • countdown.wav - Countdown beeps")
    print("  • intro.wav - Intro fanfare")
    print("\nYou're ready to play!")
    
except Exception as e:
    print(f"\n✗ Error generating audio: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
