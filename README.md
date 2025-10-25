# Windows Desktop Voice Agent

A local Windows desktop voice agent that can control your computer hands-free through voice commands.

## What it does

This project creates a voice-controlled desktop agent that can see your screen and act on it. You speak a command, and the agent will:

1. **Listen** to your voice through the microphone
2. **Transcribe** your speech to text using Whisper
3. **Screenshot** your current screen
4. **Plan** what action to take by analyzing the screenshot and your request
5. **Execute** the planned action using pyautogui (clicking, typing, scrolling)
6. **Repeat** the process for multi-step tasks

## High-level operation loop

The agent follows this continuous loop:

1. **Listen** - Record audio from microphone until you stop speaking
2. **Transcribe** - Convert speech to text using OpenAI Whisper
3. **Screenshot** - Capture full-screen image of current state
4. **Plan** - Send screenshot + request + action history to AI planner
5. **Execute** - Perform the planned UI action (click, type, scroll)
6. **Repeat** - Continue the loop for hands-free computer control

## AI Planner

We plan to integrate **Gemini 2.5 Computer Use** as the AI planner model, which can analyze screenshots and return structured UI actions. Currently, the planner is implemented as a stub with rule-based fallback logic for local testing.

## Requirements

- Windows 10/11
- Python 3
- Microphone access
- No admin privileges required

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
cd src
python main.py
```

Then speak your commands to control your desktop hands-free!
