"""
Main voice-controlled desktop agent.

This is the main orchestration loop that coordinates all modules:
1. Listen to voice commands
2. Transcribe speech to text
3. Capture screen state
4. Plan UI actions with AI
5. Execute actions on desktop
6. Maintain interaction history
7. Repeat forever

The user interacts only through voice - no keyboard input required.
"""

import sys
import time
from typing import List, Dict

# Add src directory to path for sibling imports
sys.path.append('.')

from audio_listener import record_command
from speech_to_text import transcribe_audio
from screen_capture import capture_screen
from gemini_client import propose_action
from action_executor import execute_action_plan


def main():
    """
    Main voice control loop for the desktop agent.
    
    Continuously listens for voice commands and executes UI actions
    based on AI planning until interrupted by Ctrl+C.
    """
    # Initialize interaction history
    history: List[Dict] = []
    
    # Startup banner
    print("=" * 60)
    print("[agent] voice-controlled desktop agent online")
    print("[agent] Press Ctrl+C to quit")
    print("=" * 60)
    
    try:
        while True:
            print("\n[agent] speak a command...")
            
            # 1. Listen to voice until silence
            audio_samples = record_command()
            
            # Skip if no audio captured
            if len(audio_samples) == 0:
                print("[agent] no audio captured, retrying...")
                continue
            
            # 2. Convert speech to text
            user_text = transcribe_audio(audio_samples)
            if not user_text:
                print("[agent] could not understand speech, retrying.")
                continue
            print(f"[agent] understood command: {user_text}")
            
            # 3. Capture current screen state
            png_bytes, screen_size = capture_screen()
            
            # Skip if screenshot failed
            if len(png_bytes) == 0:
                print("[agent] failed to capture screen, retrying...")
                continue
            
            # 4. Plan the next UI action
            plan = propose_action(
                user_request=user_text,
                screenshot_png=png_bytes,
                screen_size=screen_size,
                history=history,
                audio_samples=audio_samples
            )
            
            # 5. Check if we have an actionable plan
            if plan.get("action_type") == "none":
                print("[agent] no actionable plan. waiting for next command.")
                continue
            
            # 6. Execute the planned action
            print(f"[agent] executing plan: {plan}")
            execute_action_plan(plan)
            
            # 7. Save interaction to history
            history.append({
                "user_request": user_text,
                "action_taken": plan
            })
            
            # 8. Brief pause to prevent immediate re-triggering
            time.sleep(0.5)
            
            # Show history length for debugging
            print(f"[agent] history length: {len(history)}")
    
    except KeyboardInterrupt:
        print("\n[agent] shutting down...")
        print(f"[agent] total interactions: {len(history)}")
        print("[agent] goodbye!")
    
    except Exception as e:
        print(f"[agent] unexpected error: {e}")
        print("[agent] restarting loop...")
        # Could add retry logic here if needed


if __name__ == "__main__":
    main()
