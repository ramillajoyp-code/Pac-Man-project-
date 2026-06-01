import wave
import os
import math

def create_beep_sound(filename, frequency=880, duration=0.2, sample_rate=44100):
    """Create a simple beep sound without numpy"""
    num_samples = int(sample_rate * duration)
    
    waveform = []
    for i in range(num_samples):
        t = i / sample_rate
        # Generate sine wave
        sample = math.sin(2 * math.pi * frequency * t)
        # Apply envelope (simple fade in/out)
        if i < sample_rate * 0.01:  # Fade in
            sample *= (i / (sample_rate * 0.01))
        elif i > num_samples - sample_rate * 0.01:  # Fade out
            sample *= ((num_samples - i) / (sample_rate * 0.01))
        # Convert to 16-bit PCM
        sample_int = int(sample * 32767)
        sample_int = max(-32768, min(32767, sample_int))  # Clamp to 16-bit range
        waveform.append(sample_int)
    
    # Write to WAV file
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        for sample in waveform:
            wav_file.writeframes(sample.to_bytes(2, byteorder='little', signed=True))

def create_intro_sound(filename, sample_rate=44100):
    """Create a Pac-Man inspired energetic intro sound"""
    # Classic Pac-Man intro melody pattern
    # Starts with iconic descending notes, then playful bouncy pattern
    notes = [
        # Opening riff - descending (iconic Pac-Man sound)
        (784, 0.12),    # G5 - classic opening
        (659, 0.12),    # E5
        (523, 0.12),    # C5
        (392, 0.12),    # G4
        
        # Ascending playful bounce (characteristic Pac-Man energy)
        (440, 0.10),    # A4
        (494, 0.10),    # B4
        (523, 0.10),    # C5
        (587, 0.10),    # D5
        (659, 0.10),    # E5
        
        # Mini riff
        (523, 0.08),    # C5 - quick note
        (659, 0.08),    # E5
        
        # Grand finale - high energetic ending
        (784, 0.15),    # G5
        (880, 0.15),    # A5
        (1047, 0.25),   # C6 - held longer for impact
    ]
    
    waveform = []
    
    for frequency, duration in notes:
        num_samples = int(sample_rate * duration)
        for i in range(num_samples):
            t = i / sample_rate
            # Generate sine wave for retro arcade feel
            sample = math.sin(2 * math.pi * frequency * t)
            
            # Apply smooth envelope for cleaner sound
            if i < sample_rate * 0.02:  # Fade in
                sample *= (i / (sample_rate * 0.02))
            elif i > num_samples - sample_rate * 0.03:  # Fade out
                sample *= ((num_samples - i) / (sample_rate * 0.03))
            
            # Convert to 16-bit PCM
            sample_int = int(sample * 32767 * 0.8)
            sample_int = max(-32768, min(32767, sample_int))
            waveform.append(sample_int)
        
        # Add minimal silence between notes for tight rhythm
        silence_samples = int(sample_rate * 0.03)
        for _ in range(silence_samples):
            waveform.append(0)
    
    # Write to WAV file
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        for sample in waveform:
            wav_file.writeframes(sample.to_bytes(2, byteorder='little', signed=True))

# Create sounds directory if it doesn't exist
os.makedirs("assets/sounds", exist_ok=True)

# Create start button sound (higher pitch, longer)
create_beep_sound("assets/sounds/start_button.wav", frequency=1047, duration=0.5)
print("✓ Created start_button.wav")

# Create countdown beep (medium pitch)
create_beep_sound("assets/sounds/countdown.wav", frequency=880, duration=0.2)
print("✓ Created countdown.wav")

# Create intro sound (energetic fanfare)
create_intro_sound("assets/sounds/intro.wav")
print("✓ Created intro.wav")

print("\nAll sound files created successfully!")
