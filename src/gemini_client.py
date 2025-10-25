"""
Gemini AI planner module - currently stubbed for local testing.

TODO: Replace this stub with an actual call to Gemini 2.5 Computer Use API.

The real implementation will:
1. Send the screenshot PNG bytes, user's spoken goal, and recent action history to Gemini 2.5 Computer Use
2. Gemini will analyze the screenshot and respond with structured UI actions (click_at, type_text_at, scroll, etc.)
3. Parse Gemini's response into the standardized dict format used by action_executor.py
4. Feed the new screenshot + updated history back into Gemini to iterate through multi-step tasks
5. Implement proper supervision for risky actions as recommended by Google

This creates the complete Computer Use agent loop:
screenshot + goal + history → Gemini → UI action → execute → new screenshot → repeat
"""

from typing import Dict, List, Tuple


def propose_action(user_request: str,
                   screenshot_png: bytes,
                   screen_size: Tuple[int, int],
                   history: List[Dict]) -> Dict:
    """
    Propose the next UI action based on user request and screen state.
    
    Currently implements rule-based fallback logic. Will be replaced with
    Gemini 2.5 Computer Use API calls.
    
    Args:
        user_request: The user's spoken command (lowercase)
        screenshot_png: PNG bytes of current screen (not used in stub)
        screen_size: (width, height) of the screen
        history: List of previous user_request + action_taken pairs
        
    Returns:
        Dict: Action to execute with standardized format
    """
    # Log the incoming request
    print(f"[planner] request: {user_request}")
    
    # Lowercase the request for consistent matching
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
    # Test the planner with various inputs
    print("Testing Gemini client planner (stubbed)...")
    
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
