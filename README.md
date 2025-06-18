# Meeting Transcriber
A Python tool for recording and transcribing meetings using OpenAI Whisper, with a simple always-on-top GUI for easy start/stop.  
**Supports rapid deployment and includes optional installers for VB-Cable and Voicemeeter in the `ext` folder.**

---

## Features
- Record meeting audio in 1-minute chunks
- Transcribe audio automatically using Whisper
- Simple GUI for starting/stopping recording (always on top)
- Outputs transcript as a timestamped `.txt` file
- Optional: Install VB-Cable and Voicemeeter from the GUI (if using the config version)

---

## Quick Start

### 1. Clone the Repository
```sh
git clone https://github.com/yourusername/meeting-transcriber.git
cd meeting-transcriber
```

### 2. Install Dependencies
```sh
pip install -r requirements.txt
```

### 3. (Optional) Install Audio Routing Tools
If you want to capture system/meeting audio, install [VB-Cable](https://vb-audio.com/Cable/) and [Voicemeeter](https://vb-audio.com/Voicemeeter/).  
Installers are provided in the `ext` folder for convenience.

### 4. Run the Transcriber
```sh
python transcriber.py
```
- Use the GUI window to start and stop recording.  
- The transcript will be saved as a file like `17JUN2025_1530.txt` in the same folder.

---

## Usage Notes
- **Set your meeting audio output** to "CABLE Input" (VB-Cable) so the script can capture it.  
- The tool will process and transcribe audio in the background while recording.  
- The GUI is always on top for quick access.

---

## Deploy as an Executable
You can build a standalone `.exe` using PyInstaller:
```sh
pyinstaller --onefile --windowed --add-data "ext;ext" transcriber.py
```

---

## Folder Structure
```
transcriber/
├── transcriber.py
├── requirements.txt
├── README.md
├── ext/
│   ├── VBCABLE_Driver_Pack45/
│   └── VoicemeeterSetup_v1119/
```

---

## Requirements
- Python 3.8+  
- See `requirements.txt` for Python dependencies

---

## Credits
- [OpenAI Whisper](https://github.com/openai/whisper)  
- [VB-Audio](https://vb-audio.com/) for VB-Cable and Voicemeeter

---

## License
This project is for personal/internal use.  
**Do not redistribute the VB-Cable or Voicemeeter installers outside their license terms.**