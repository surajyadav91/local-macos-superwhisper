# Local macOS SuperWhisper

A local macOS speech-to-text application that uses NVIDIA's Parakeet model to transcribe audio and automatically paste the text wherever your cursor is located.

> **Note**: This was developed quickly using LLMs and AI-assisted coding. There may be bugs or areas for improvement. Feel free to contribute or report issues!

## Features

- **Local Processing**: All transcription happens locally on your Mac - no data sent to external servers
- **Hotkey Control**: Start/stop recording with customizable keyboard shortcuts (default: Cmd+Option+;)
- **Auto-Paste**: Transcribed text automatically appears at your cursor location
- **NVIDIA Parakeet**: Uses state-of-the-art NVIDIA Parakeet model for accurate transcription
- **Menu Bar Integration**: Clean macOS menu bar interface using rumps

## Inspiration

SuperWhisper offers NVIDIA Parakeet as one of its transcription models while the model runs locally, SuperWhisper requires a purchase to use. This project provides a free, local alternative using Parakeet model for personal use.

## Setup

### Prerequisites
- macOS
- Python 3.12
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/surajyadav91/local-macos-superwhisper.git
   cd local-macos-superwhisper
   ```

2. **Install dependencies:**
Use uv package manager to install dependencies

3. **First run setup:**
   ```bash
   uv run python speech_to_text.py
   ```

## First Time Setup

### Model Download
On first run, the application will download the NVIDIA Parakeet model. This may take a few minutes depending on your internet connection.

### Permissions Required
The app will request the following macOS permissions:
- **Accessibility**: Required to capture hotkey combinations
- **Microphone**: Required to record audio
- **Input Monitoring**: Required to paste text automatically

## Usage

1. **Start the application:**
   ```bash
   uv run python speech_to_text.py
   ```

2. **Recording:**
   - Press `Cmd+Option+;` to start recording
   - Speak clearly into your microphone
   - Press `Cmd+Option+;` again to stop recording

3. **Auto-paste:**
   - Place your cursor where you want the text to appear
   - The transcribed text will automatically be pasted at the cursor location

## Configuration

### Changing Hotkeys
Edit the hotkey combination in `speech_to_text.py`

### Changing Model
You can change the model by editing the `speech_to_text.py` file with a few lines of code change

## Use Cases

- **AI Prompting**: Perfect for long ChatGPT, Claude, Cursor or other AI chat sessions - speak your prompts instead of typing

**Example workflow**: Instead of typing a lengthy prompt to ChatGPT, simply press the hotkey, speak your question naturally, and the transcribed text appears in the chat box ready to send.
