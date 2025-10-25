"""
Local speech-to-text module using OpenAI Whisper.

This module provides local speech transcription using the Whisper "small" model.
Currently uses Whisper for offline transcription, but may be swapped out for
Gemini audio models in the future for better integration with the AI planner.
"""

import numpy as np
import whisper

# Load Whisper model once at module import
print("[whisper] Loading Whisper 'small' model...")
model = whisper.load_model("small")
print("[whisper] Model loaded successfully")


def transcribe_audio(audio_samples: np.ndarray) -> str:
    """
    Transcribe audio samples to text using Whisper.
    
    Args:
        audio_samples: NumPy array of float32 audio samples at 16 kHz mono
        
    Returns:
        str: Lowercase transcribed text, or empty string if transcription fails
    """
    try:
        # Ensure audio is float32, 16 kHz mono
        if audio_samples.dtype != np.float32:
            audio_samples = audio_samples.astype(np.float32)
        
        # Transcribe using Whisper
        result = model.transcribe(
            audio_samples,
            fp16=False,
            language="en"
        )
        
        # Extract text and clean it up
        text = result["text"].lower().strip()
        
        # Log the transcription
        print(f"[voice] transcribed: {text}")
        
        return text
        
    except Exception as e:
        print(f"[error] Transcription failed: {e}")
        return ""


if __name__ == "__main__":
    # Test the transcription with a simple example
    print("Testing speech-to-text module...")
    
    # Create a simple test audio signal (sine wave)
    duration = 1.0  # seconds
    sample_rate = 16000
    frequency = 440  # Hz (A note)
    
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    test_audio = np.sin(2 * np.pi * frequency * t).astype(np.float32)
    
    print(f"Created test audio: {len(test_audio)} samples")
    print("Note: This is just a sine wave, not actual speech.")
    print("For real testing, use audio_listener.py to record actual speech.")
    
    # Test transcription (will likely return empty or gibberish for sine wave)
    result = transcribe_audio(test_audio)
    print(f"Transcription result: '{result}'")
