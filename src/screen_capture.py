"""
Screen capture module for full-screen screenshots.

This module provides functionality to capture the primary monitor's screen
and return it as PNG bytes in memory for processing by the AI planner.
"""

import io
from PIL import ImageGrab
from typing import Tuple


def capture_screen() -> Tuple[bytes, Tuple[int, int]]:
    """
    Capture a full-screen screenshot of the primary monitor.
    
    Returns:
        Tuple[bytes, Tuple[int, int]]: PNG bytes and (width, height) dimensions
    """
    try:
        # Capture the full screen using PIL
        screenshot = ImageGrab.grab()
        
        # Get dimensions
        width, height = screenshot.size
        
        # Convert to PNG bytes in memory
        png_buffer = io.BytesIO()
        screenshot.save(png_buffer, format='PNG')
        png_bytes = png_buffer.getvalue()
        
        # Log the capture
        print(f"[screen] captured {width}x{height}")
        
        return png_bytes, (width, height)
        
    except Exception as e:
        print(f"[error] Screen capture failed: {e}")
        # Return empty bytes and zero dimensions on failure
        return b'', (0, 0)


if __name__ == "__main__":
    # Test the screen capture
    print("Testing screen capture...")
    
    try:
        png_data, dimensions = capture_screen()
        width, height = dimensions
        
        print(f"Captured screenshot: {width}x{height}")
        print(f"PNG data size: {len(png_data)} bytes")
        
        if len(png_data) > 0:
            print("✓ Screen capture successful!")
        else:
            print("✗ Screen capture failed - no data returned")
            
    except Exception as e:
        print(f"Test failed: {e}")
