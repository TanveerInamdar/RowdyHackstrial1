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
from typing import Dict, List, Tuple
from google import genai
from google.genai import types


def propose_action(user_request: str,
                   screenshot_png: bytes,
                   screen_size: Tuple[int, int],
                   history: List[Dict]) -> Dict:
    """
    Propose the next UI action using Gemini 2.5 Computer Use API.
    
    Args:
        user_request: The user's spoken command
        screenshot_png: PNG bytes of current screen
        screen_size: (width, height) of the screen
        history: List of previous user_request + action_taken pairs
        
    Returns:
        Dict: Action to execute with standardized format
    """
    # Log the incoming request
    print(f"[planner] request: {user_request}")
    
    try:
        # Initialize Gemini client
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        
        # Convert screenshot to base64 for API
        screenshot_base64 = base64.b64encode(screenshot_png).decode('utf-8')
        
        # Build conversation history for context
        history_context = ""
        if history:
            history_context = "\n\nRecent actions:\n"
            for i, item in enumerate(history[-3:]):  # Last 3 actions for context
                history_context += f"{i+1}. User: {item['user_request']}\n"
                history_context += f"   Action: {item['action_taken']}\n"
        
        # Create the prompt for Computer Use
        prompt = f"""You are a Computer Use agent that can see and interact with a Windows desktop screen.

User's current request: "{user_request}"
{history_context}

Analyze the screenshot and determine the next UI action to fulfill the user's request.

Available actions:
- click(x, y): Click at specific coordinates
- type_text(text): Type text at current cursor position
- key(key_name): Press a key (win, enter, tab, etc.)
- scroll(direction, amount): Scroll up/down/left/right
- none: No action needed

Respond with a JSON object containing:
{{
    "action_type": "click|type_text|key|scroll|none",
    "x": <int>,  // for click actions
    "y": <int>,  // for click actions  
    "text": "<string>",  // for type_text actions
    "key": "<string>",  // for key actions
    "direction": "<string>",  // for scroll actions (up/down/left/right)
    "amount": <int>,  // for scroll actions
    "reasoning": "<string>",  // brief explanation of why this action
    "needs_confirmation": false  // set to true for risky actions
}}

Focus on the user's request and provide the most direct action to accomplish it."""

        # Create the Computer Use request
        response = client.models.generate_content(
            model="gemini-2.5-computer-use-preview-10-2025",
            contents=[
                types.Content(
                    parts=[
                        types.Part(text=prompt),
                        types.Part(
                            inline_data=types.InlineData(
                                mime_type="image/png",
                                data=screenshot_base64
                            )
                        )
                    ]
                )
            ],
            tools=[types.Tool(computer_use=types.ComputerUse())],
            config=types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=1000
            )
        )
        
        # Parse the response
        if response.candidates and response.candidates[0].content:
            content = response.candidates[0].content.parts[0].text
            
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
                    action = convert_gemini_action_to_standard(action_data)
                    print(f"[planner] plan: {action}")
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


def convert_gemini_action_to_standard(gemini_action: Dict) -> Dict:
    """
    Convert Gemini Computer Use action format to our standard format.
    
    Args:
        gemini_action: Action dict from Gemini API
        
    Returns:
        Dict: Standardized action format
    """
    action_type = gemini_action.get("action_type", "none")
    
    if action_type == "click":
        return {
            "action_type": "click",
            "x": gemini_action.get("x", 0),
            "y": gemini_action.get("y", 0),
            "needs_confirmation": gemini_action.get("needs_confirmation", False)
        }
    elif action_type == "type_text":
        return {
            "action_type": "type_text",
            "text": gemini_action.get("text", ""),
            "needs_confirmation": gemini_action.get("needs_confirmation", False)
        }
    elif action_type == "key":
        return {
            "action_type": "key",
            "key": gemini_action.get("key", ""),
            "needs_confirmation": gemini_action.get("needs_confirmation", False)
        }
    elif action_type == "scroll":
        # Convert scroll to sequence of key presses
        direction = gemini_action.get("direction", "down")
        amount = gemini_action.get("amount", 3)
        
        steps = []
        for _ in range(min(amount, 5)):  # Limit scroll amount
            if direction == "up":
                steps.append({"action_type": "key", "key": "up"})
            elif direction == "down":
                steps.append({"action_type": "key", "key": "down"})
            elif direction == "left":
                steps.append({"action_type": "key", "key": "left"})
            elif direction == "right":
                steps.append({"action_type": "key", "key": "right"})
        
        return {
            "action_type": "sequence",
            "steps": steps,
            "needs_confirmation": gemini_action.get("needs_confirmation", False)
        }
    else:
        return {
            "action_type": "none",
            "needs_confirmation": False
        }


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
