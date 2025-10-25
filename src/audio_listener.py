"""
Audio listener module for voice command recording.

This module provides voice activity detection and continuous recording
from the default microphone until the user stops talking.
"""

import numpy as np
import sounddevice as sd
import time
import signal
import sys
from typing import List

# Audio recording constants
SAMPLE_RATE = 16000
CHANNELS = 1
SILENCE_SECONDS = 1.0
ENERGY_THRESHOLD = 0.01

# Minimum audio duration before we start looking for silence
MIN_AUDIO_SECONDS = 0.5


def record_command() -> np.ndarray:
    """
    Record audio from the default microphone until voice activity stops.
    
    Uses simple energy-based voice activity detection:
    - Records continuously while energy > threshold
    - After minimum audio duration, starts silence timer
    - Stops recording after sustained silence period
    
    Returns:
        np.ndarray: Float32 audio samples at 16 kHz mono, shape (N,)
    """
    print("[listening...]")
    
    audio_chunks: List[np.ndarray] = []
    silence_start_time = None
    total_audio_time = 0.0
    
    # Global flag for graceful interruption
    interrupted = False
    
    def signal_handler(signum, frame):
        nonlocal interrupted
        interrupted = True
        print("\n[interrupted]")
    
    # Set up Ctrl+C handler
    original_handler = signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Open audio stream
        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype=np.float32,
            blocksize=1024
        ) as stream:
            
            while not interrupted:
                # Read audio chunk
                audio_chunk, overflowed = stream.read(1024)
                
                if overflowed:
                    print("[warning] audio buffer overflow")
                
                # Flatten chunk to 1D array
                audio_chunk = audio_chunk.flatten()
                audio_chunks.append(audio_chunk)
                
                # Calculate energy (mean absolute value)
                energy = np.mean(np.abs(audio_chunk))
                chunk_duration = len(audio_chunk) / SAMPLE_RATE
                total_audio_time += chunk_duration
                
                # Voice activity detection logic
                if energy < ENERGY_THRESHOLD:
                    # Low energy - potentially silence
                    if total_audio_time >= MIN_AUDIO_SECONDS:
                        # We've heard enough audio, start silence timer
                        if silence_start_time is None:
                            silence_start_time = time.time()
                        else:
                            # Check if we've been silent long enough
                            silence_duration = time.time() - silence_start_time
                            if silence_duration >= SILENCE_SECONDS:
                                # Stop recording
                                break
                    else:
                        # Not enough audio yet, reset silence timer
                        silence_start_time = None
                else:
                    # High energy - voice detected, reset silence timer
                    silence_start_time = None
    
    except KeyboardInterrupt:
        interrupted = True
        print("\n[interrupted]")
    
    finally:
        # Restore original signal handler
        signal.signal(signal.SIGINT, original_handler)
    
    # Concatenate all audio chunks
    if audio_chunks:
        full_audio = np.concatenate(audio_chunks)
        # Ensure float32 and proper shape
        full_audio = full_audio.astype(np.float32).flatten()
        print(f"[heard command] ({len(full_audio)/SAMPLE_RATE:.1f}s)")
        return full_audio
    else:
        print("[no audio captured]")
        return np.array([], dtype=np.float32)


if __name__ == "__main__":
    # Test the audio recording
    print("Testing audio recording...")
    print("Speak something, then stay quiet for 1 second to stop.")
    print("Press Ctrl+C to interrupt early.")
    
    try:
        audio = record_command()
        print(f"Recorded {len(audio)} samples ({len(audio)/SAMPLE_RATE:.2f} seconds)")
        print(f"Audio range: [{np.min(audio):.3f}, {np.max(audio):.3f}]")
    except Exception as e:
        print(f"Error: {e}")
