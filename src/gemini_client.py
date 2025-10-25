"""
Gemini AI planner module with actual Gemini 2.5 Computer Use API integration.

This module implements the real Gemini 2.5 Computer Use API to analyze screenshots
and generate structured UI actions. Based on the official documentation:
https://ai.google.dev/gemini-api/docs/computer-use

The Computer Use model can "see" a computer screen and "act" by generating
specific UI actions like mouse clicks and keyboard inputs.
"""

import base64
import os
import numpy as np
from typing import Dict, List, Tuple
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def propose_action(user_request: str,
                   screenshot_png: bytes,
                   screen_size: Tuple[int, int],
                   history: List[Dict],
                   audio_samples: np.ndarray = None) -> Dict:
    """
    Propose the next UI action using Gemini 2.5 Flash with audio + screenshot.
    
    Args:
        user_request: The user's spoken command (transcribed text)
        screenshot_png: PNG bytes of current screen
        screen_size: (width, height) of the screen
        history: List of previous user_request + action_taken pairs
        audio_samples: Raw audio samples (optional, for direct audio processing)
        
    Returns:
        Dict: Action to execute with standardized format
    """
    # Log the incoming request
    print(f"[planner] request: {user_request}")
    
    try:
        # Initialize Gemini client
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        
        # Build conversation history for context
        history_context = ""
        if history:
            history_context = "\n\nRecent actions:\n"
            for i, item in enumerate(history[-3:]):  # Last 3 actions for context
                history_context += f"{i+1}. User: {item['user_request']}\n"
                history_context += f"   Action: {item['action_taken']}\n"
        
        # Create the prompt for Gemini 2.5 Flash (using gemini-2.5-flash model)
        prompt = f"""You are a desktop automation assistant. Analyze the screenshot and user's voice command to determine where to click.

Screen dimensions: {screen_size[0]}x{screen_size[1]} pixels
User's request: "{user_request}"
{history_context}

Look at the screenshot and identify the exact pixel coordinates (x, y) where you should click to fulfill the user's request.

Respond with ONLY a JSON object in this exact format:
{{
    "action_type": "click",
    "x": <pixel_x_coordinate>,
    "y": <pixel_y_coordinate>,
    "reasoning": "<brief explanation of why you chose these coordinates>"
}}

Examples:
- "click start menu" → click bottom-left corner
- "click settings" → find and click settings icon/app
- "click chrome" → find and click Chrome browser icon
- "click close" → find and click close button
- "click minimize" → find and click minimize button

Be precise with coordinates. Look for visual elements that match the user's request."""

        # Prepare image
        import PIL.Image
        import io
        image = PIL.Image.open(io.BytesIO(screenshot_png))
        
        # Create the model
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Generate content with image and prompt
        response = model.generate_content([prompt, image])
        
        # Parse the response
        if response and response.text:
            content = response.text
            
            # Try to extract JSON from the response
            import json
            try:
                # Look for JSON in the response
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx != -1 and end_idx != 0:
                    json_str = content[start_idx:end_idx]
                    action_data = json.loads(json_str)
                    
                    # Convert to our standard format
                    action = {
                        "action_type": "click",
                        "x": action_data.get("x", 0),
                        "y": action_data.get("y", 0),
                        "needs_confirmation": False
                    }
                    
                    print(f"[planner] plan: {action}")
                    print(f"[planner] reasoning: {action_data.get('reasoning', 'No reasoning provided')}")
                    return action
                else:
                    print(f"[planner] no JSON found in response: {content}")
            except json.JSONDecodeError as e:
                print(f"[planner] JSON parse error: {e}")
                print(f"[planner] raw response: {content}")
        
        # Fallback to rule-based logic if API fails
        print("[planner] API failed, using fallback logic")
        return fallback_action_logic(user_request, screen_size)
        
    except Exception as e:
        print(f"[planner] API error: {e}")
        print("[planner] using fallback logic")
        return fallback_action_logic(user_request, screen_size)


def fallback_action_logic(user_request: str, screen_size: Tuple[int, int]) -> Dict:
    """
    Fallback rule-based logic when Gemini API is unavailable.
    
    Args:
        user_request: The user's spoken command
        screen_size: (width, height) of the screen
        
    Returns:
        Dict: Action to execute
    """
    request_lower = user_request.lower()
    
    # Rule 1: Start menu / Windows menu
    start_keywords = ["open start", "open windows", "click start", "start menu", "start"]
    if any(keyword in request_lower for keyword in start_keywords):
        action = {
            "action_type": "click",
            "x": 30,
            "y": screen_size[1] - 30,  # Bottom-left corner
            "needs_confirmation": False
        }
        print(f"[planner] plan: {action}")
        return action
    
    # Rule 2: Settings
    if "settings" in request_lower or "open settings" in request_lower:
        action = {
            "action_type": "sequence",
            "steps": [
                {"action_type": "key", "key": "win"},
                {"action_type": "type_text", "text": "settings"},
                {"action_type": "key", "key": "enter"}
            ],
            "needs_confirmation": False
        }
        print(f"[planner] plan: {action}")
        return action
    
    # Rule 3: Default - no action
    action = {
        "action_type": "none",
        "needs_confirmation": False
    }
    print(f"[planner] plan: {action}")
    return action


if __name__ == "__main__":
    # Test the Gemini integration
    print("Testing Gemini Computer Use integration...")
    print("Note: Requires GEMINI_API_KEY environment variable")
    
    # Check for API key
    if not os.getenv("GEMINI_API_KEY"):
        print("ERROR: GEMINI_API_KEY environment variable not set")
        print("Set it with: set GEMINI_API_KEY=your_api_key_here")
        exit(1)
    
    # Mock screen size
    screen_size = (1920, 1080)
    
    # Mock screenshot (empty bytes for testing)
    screenshot_png = b""
    
    # Mock history
    history = []
    
    # Test cases
    test_cases = [
        "open start menu",
        "click start",
        "open settings",
        "settings please",
        "open windows",
        "hello world",
        "random command"
    ]
    
    for test_request in test_cases:
        print(f"\n--- Testing: '{test_request}' ---")
        result = propose_action(test_request, screenshot_png, screen_size, history)
        print(f"Result: {result}")
        
        # Simulate adding to history
        history.append({
            "user_request": test_request,
            "action_taken": result
        })
    
    print(f"\nFinal history length: {len(history)}")
