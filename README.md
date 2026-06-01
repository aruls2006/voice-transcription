# Smart Meeting Note Generator - Windows Desktop App

## Quick Start
1. Make sure **Python 3.8+** is installed on your computer ([python.org](https://python.org)).
2. Double-click **`Start SMNG.bat`** to launch the application.
3. The app will open automatically in Microsoft Edge as a desktop window.

## Requirements
- Windows 10 or later
- Python 3.8+ (required for voice-to-text transcription)
- Internet connection (for AI-powered meeting analysis via OpenRouter)

## How It Works
- **Record meetings** using your microphone or by capturing Google Meet / Zoom / Teams audio
- **Automatic transcription** converts speech to text using Google Speech API (via Python)
- **AI analysis** generates meeting summaries, action items, decisions, and sentiment using the OpenRouter API (nvidia/nemotron free reasoning model)
- **API key** is pre-encrypted in `database.json` — no manual setup needed

## Files
| File | Purpose |
|------|---------|
| `SmartMeetingNotes.exe` | The application server (compiled Node.js) |
| `Start SMNG.bat` | Launcher — double-click this to start |
| `transcribe.py` | Voice-to-text transcription engine |
| `database.json` | Encrypted settings and meeting data |
| `web/` | Frontend user interface files |
| `uploads/` | Recorded audio files storage |

## Headphones & Google Meet Tip
When wearing headphones during a Google Meet call:
1. Open `http://localhost:5050` in a **normal Chrome/Edge tab** (same browser as your meeting)
2. In SMNG, choose **"Google Meet / System Audio Capture"** mode
3. Select your **Google Meet tab** and check **"Share tab audio"** in the browser popup
4. Both your voice and the other participants' voices will be captured

## Troubleshooting
- **"Python not found" warning**: Install Python from [python.org](https://python.org) and ensure "Add to PATH" is checked during installation.
- **Port 5050 in use**: Close any other instance of SMNG, or check for processes using port 5050.
- **Transcription empty**: Ensure `SpeechRecognition` Python package is installed (`pip install SpeechRecognition`).
