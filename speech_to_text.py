
"""macOS speech to text

Run this file and a small microphone icon will appear in the macOS menu
bar.

Press command + option + ; to start/stop recording. (option + ; becomes …)

"""
from __future__ import annotations

import os
import queue
from datetime import datetime

import numpy as np
import rumps
import sounddevice as sd
import soundfile as sf
from pynput import keyboard
import subprocess
import torch
import nemo.collections.asr as nemo_asr

# Pick best device
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"

_asr_model = nemo_asr.models.ASRModel.from_pretrained(
    model_name="nvidia/parakeet-tdt-0.6b-v2"
).to(DEVICE)

# ---------------------- CONFIG ---------------------------------------
AUDIO_SAMPLE_RATE = 16_000
CHANNELS = 1
HOTKEY_RUMPS = "command+option+…"      # command + option + ; (option + ; becomes …)
HOTKEY_PYNPUT = "<cmd>+<alt>+…"      
OUT_DIR = os.path.expanduser("~/Recordings")
# Constant output path (overwritten each time)
REC_WAV = os.path.join(OUT_DIR, "rec.wav")
# ---------------------------------------------------------------------

_audio_q: "queue.Queue[np.ndarray]" = queue.Queue()
_recording: bool = False
_stream: sd.InputStream | None = None


# ---------------------- AUDIO HELPERS --------------------------------

def _audio_callback(indata: np.ndarray, frames: int, time, status):
    if status:
        print("[audio]", status, flush=True)
    _audio_q.put(indata.copy())


def _start_recording(app: "RecorderApp") -> None:
    global _recording, _stream
    if _recording:
        return
    while not _audio_q.empty():
        _audio_q.get_nowait()

    _stream = sd.InputStream(
        samplerate=AUDIO_SAMPLE_RATE,
        channels=CHANNELS,
        callback=_audio_callback,
    )
    _stream.start()
    _recording = True
    app.title = "🔴"  # red dot indicator
    _notify("Recorder", "Recording started", "Press ⌘⌥; again to stop")
    os.system("afplay /System/Library/Sounds/Pop.aiff &")


def _stop_recording(app: "RecorderApp") -> None:
    global _recording, _stream
    if not _recording:
        return
    _stream.stop()
    _stream.close()
    _stream = None
    _recording = False
    app.title = "🎤"
    os.system("afplay /System/Library/Sounds/Pop.aiff &")

    blocks: list[np.ndarray] = []
    while not _audio_q.empty():
        blocks.append(_audio_q.get())
    if not blocks:
        _notify("Recorder", "No audio", "Nothing captured")
        return
    audio_data = np.concatenate(blocks, axis=0)
    os.makedirs(OUT_DIR, exist_ok=True)
    sf.write(REC_WAV, audio_data, AUDIO_SAMPLE_RATE)

    # Transcribe on selected device under inference mode
    with torch.inference_mode():
        transcript = _asr_model.transcribe([REC_WAV])[0].text

    # Copy to clipboard and paste into frontmost app
    try:
        subprocess.run("pbcopy", input=transcript.encode(), check=True)
        # Simulate Cmd+V to paste
        os.system(
            "osascript -e 'tell application \"System Events\" to keystroke \"v\" using {command down}'"
        )
    except Exception as exc:
        print(f"Clipboard/paste failed: {exc}")

    _notify(
        "Recorder",
        "Saved & Transcribed",
        (transcript[:60] + "…") if len(transcript) > 60 else transcript,
    )


# ---------------------- SAFE NOTIFICATION WRAPPER -----------------------------

def _notify(title: str, subtitle: str = "", message: str = ""):
    """Send a macOS notification if possible, else fallback to stdout."""
    try:
        rumps.notification(title, subtitle, message)
    except Exception as exc:  # missing Info.plist or other
        print(f"[notify] {title}: {subtitle} {message} ({exc})")


# ---------------------- APP ------------------------------------------

class RecorderApp(rumps.App):
    def __init__(self):
        super().__init__(
            name="Recorder",
            menu=["Toggle Recording", "Quit"],
        )
        self.title = "🎤"  # show mic emoji in menu bar
        # Start pynput global hotkey listener in background
        listener = keyboard.GlobalHotKeys({HOTKEY_PYNPUT: self.on_hotkey})
        listener.start()
        # Also register menu-bar shortcut in rumps itself (if version supports)
        try:
            self.key = HOTKEY_RUMPS
        except AttributeError:
            pass

    # Menu item & hotkey share the same handler
    def on_hotkey(self, _=None):
        if _recording:
            _stop_recording(self)
        else:
            _start_recording(self)

    @rumps.clicked("Toggle Recording")
    def menu_toggle(self, _):
        self.on_hotkey()

    @rumps.clicked("Quit")
    def menu_quit(self, _):
        if _recording:
            _stop_recording(self)
        rumps.quit_application()


if __name__ == "__main__":
    RecorderApp().run()
