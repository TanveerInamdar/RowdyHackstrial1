"""
Action executor module for performing UI actions using pyautogui.

This module takes action plans from the AI planner and executes them
on the Windows desktop using pyautogui automation.

TODO: In the future we will add a safety gate that asks for a spoken "yes"
before executing high-risk actions like deleting files, modifying system settings,
or performing actions that could cause data loss.
"""

import time
import pyautogui
from typing import Dict

# Set a small pause between pyautogui actions
pyautogui.PAUSE = 0.15


def execute_single_action(action: Dict) -> None:
    """
    Execute a single UI action using pyautogui.
    
    Args:
        action: Dictionary containing action_type and relevant parameters
    """
    try:
        action_type = action.get("action_type", "none")
        
        if action_type == "click":
            x = action.get("x", 0)
            y = action.get("y", 0)
            print(f"[exec] click at ({x},{y})")
            
            # Move mouse to position with smooth animation
            pyautogui.moveTo(x, y, duration=0.2)
            # Left click
            pyautogui.click()
            
        elif action_type == "type_text":
            text = action.get("text", "")
            print(f"[exec] type_text: {text}")
            
            # Type text with small interval between characters
            pyautogui.typewrite(text, interval=0.02)
            
        elif action_type == "key":
            key = action.get("key", "")
            print(f"[exec] press key: {key}")
            
            if key == "win":
                # Press Windows key
                pyautogui.hotkey("win")
            elif key == "enter":
                # Press Enter key
                pyautogui.press("enter")
            else:
                # TODO: Add support for more keys (ctrl, alt, shift, etc.)
                print(f"[exec] unsupported key: {key}")
                
        elif action_type == "none":
            print("[exec] no-op")
            
        else:
            print(f"[exec] unknown action type: {action_type}")
            
    except Exception as e:
        print(f"[exec] ERROR: {e}")


def execute_action_plan(plan: Dict) -> None:
    """
    Execute an action plan, handling both single actions and sequences.
    
    Args:
        plan: Dictionary containing either a single action or sequence of actions
    """
    try:
        action_type = plan.get("action_type", "none")
        
        if action_type == "sequence":
            steps = plan.get("steps", [])
            print(f"[exec] executing sequence with {len(steps)} steps")
            
            for i, step in enumerate(steps):
                print(f"[exec] step {i+1}/{len(steps)}")
                execute_single_action(step)
                
                # Small delay between steps for UI to react
                if i < len(steps) - 1:  # Don't sleep after last step
                    time.sleep(0.15)
                    
        else:
            # Single action
            execute_single_action(plan)
            
    except Exception as e:
        print(f"[exec] ERROR executing plan: {e}")


if __name__ == "__main__":
    # Test the action executor with various action types
    print("Testing action executor...")
    print("Note: This will perform actual UI actions on your screen!")
    print("Make sure you're ready and press Enter to continue...")
    input()
    
    # Test single actions
    test_actions = [
        {"action_type": "none"},
        {"action_type": "click", "x": 100, "y": 100},
        {"action_type": "type_text", "text": "hello world"},
        {"action_type": "key", "key": "win"},
        {"action_type": "key", "key": "enter"},
    ]
    
    print("\n--- Testing single actions ---")
    for action in test_actions:
        print(f"Testing: {action}")
        execute_single_action(action)
        time.sleep(0.5)  # Pause between tests
    
    # Test sequence
    print("\n--- Testing sequence ---")
    sequence_plan = {
        "action_type": "sequence",
        "steps": [
            {"action_type": "key", "key": "win"},
            {"action_type": "type_text", "text": "notepad"},
            {"action_type": "key", "key": "enter"}
        ]
    }
    
    print("Testing sequence (will open Notepad):")
    execute_action_plan(sequence_plan)
    
    print("\nTest completed!")
