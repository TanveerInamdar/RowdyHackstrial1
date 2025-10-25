# Windows Desktop Voice Agent

A local Windows desktop voice agent that can control your computer hands-free through voice commands using AI vision.

## What it does

This project creates a voice-controlled desktop agent that can see your screen and act on it. You speak a command, and the agent will:

1. **Listen** to your voice through the microphone
2. **Transcribe** your speech to text using Whisper
3. **Screenshot** your current screen
4. **Analyze** the screenshot and your request using Gemini 2.5 Flash AI
5. **Execute** precise UI actions using pyautogui (clicking at exact coordinates)
6. **Repeat** the process for multi-step tasks

## High-level operation loop

The agent follows this continuous loop:

1. **Listen** - Record audio from microphone until you stop speaking
2. **Transcribe** - Convert speech to text using OpenAI Whisper
3. **Screenshot** - Capture full-screen image of current state
4. **AI Analysis** - Send screenshot + audio + text to Gemini 2.5 Flash
5. **Coordinate Generation** - AI returns precise x,y coordinates to click
6. **Execute** - Perform the UI action (click at exact coordinates)
7. **Repeat** - Continue the loop for hands-free computer control

## AI Vision Integration

The system uses **Gemini 2.5 Flash** for multi-modal AI analysis:

- **Visual Input**: Full desktop screenshot (PNG)
- **Audio Input**: Raw voice recording (WAV)
- **Text Input**: Transcribed speech + action history
- **Output**: Precise pixel coordinates (x, y) for clicking

This approach provides:
- **Real AI Vision**: AI can "see" your desktop and understand what you want to click
- **Multi-Modal Understanding**: Combines audio, visual, and text for better accuracy
- **Desktop Automation**: Works on any Windows application, not just browsers
- **Precise Control**: Returns exact pixel coordinates for accurate clicking

## Features

### ✅ **Voice Control**
- Continuous voice activity detection
- Real-time speech transcription with Whisper
- Hands-free operation (no keyboard input required)

### ✅ **AI Vision**
- Screenshot analysis with Gemini 2.5 Flash
- Multi-modal input (audio + visual + text)
- Precise coordinate generation for UI elements

### ✅ **Desktop Automation**
- Click at exact pixel coordinates
- Support for any Windows application
- Fallback rule-based logic for reliability

### ✅ **Smart Planning**
- Action history tracking for context
- Multi-step task support
- Graceful error handling and fallbacks

## Requirements

- Windows 10/11
- Python 3
- Microphone access
- Gemini API key (free tier available)
- No admin privileges required

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd DesktopAI
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Get a Gemini API key:**
   - Visit [Google AI Studio](https://aistudio.google.com/)
   - Sign in with your Google account
   - Create a new API key

4. **Set up environment:**
   ```bash
   # Create env file with your API key
   echo "GEMINI_API_KEY=your_api_key_here" > src/env
   ```

## Usage

1. **Start the voice agent:**
   ```bash
   cd src
   python main.py
   ```

2. **Speak your commands:**
   - "click start menu" - Opens Windows start menu
   - "click chrome" - Clicks on Chrome browser
   - "click settings" - Opens Windows settings
   - "click close" - Closes current window
   - "click minimize" - Minimizes current window

3. **Stop the agent:**
   - Press `Ctrl+C` to quit

## Example Commands

The AI can understand and execute various voice commands:

- **System Actions**: "click start menu", "open settings", "click taskbar"
- **Application Control**: "click chrome", "click notepad", "click calculator"
- **Window Management**: "click close", "click minimize", "click maximize"
- **Custom Actions**: "click the blue button", "click the search box"

## Architecture

### **Core Modules:**

- **`audio_listener.py`** - Voice activity detection and recording
- **`speech_to_text.py`** - Whisper speech transcription
- **`screen_capture.py`** - Desktop screenshot capture
- **`gemini_client.py`** - AI vision analysis with Gemini 2.5 Flash
- **`action_executor.py`** - UI automation with pyautogui
- **`main.py`** - Main orchestration loop

### **Data Flow:**
```
Voice → Audio → Whisper → Text
                    ↓
Desktop → Screenshot → Gemini 2.5 Flash → Coordinates
                    ↓
Coordinates → pyautogui → Click Action
```

## Safety Features

- **Fallback Logic**: Rule-based actions when AI is unavailable
- **Error Handling**: Graceful degradation on API failures
- **Quota Management**: Automatic fallback when API limits reached
- **User Control**: Easy shutdown with Ctrl+C

## Troubleshooting

### **API Issues:**
- Check your `GEMINI_API_KEY` in `src/env`
- Verify API key is valid at [Google AI Studio](https://aistudio.google.com/)
- Monitor quota usage at [AI Usage Dashboard](https://ai.dev/usage)

### **Audio Issues:**
- Ensure microphone permissions are granted
- Check microphone is working in other applications
- Adjust `ENERGY_THRESHOLD` in `audio_listener.py` if needed

### **Click Accuracy:**
- AI analyzes your actual screen - speak clearly about what you want to click
- Use specific commands like "click chrome" rather than vague requests
- Check screen resolution matches AI expectations

## Contributing

This project is designed for hackathon demonstration. Key areas for enhancement:

- **Enhanced AI Prompts**: Better prompting for more accurate coordinate detection
- **Action Types**: Support for typing, scrolling, and complex sequences
- **Safety Gates**: Confirmation prompts for risky actions
- **Multi-Monitor**: Support for multiple display setups

## License

This project is created for educational and hackathon purposes. Please ensure responsible use of AI automation tools.
