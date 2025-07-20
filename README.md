# sound-to-text — voice input with Whisper.cpp
sound-to-text — a local Windows application for speech recognition and text input simulation. It works on the basis of [whisper.cpp](https://github.com/ggml-org/whisper.cpp), uses hotkeys to activate recording, displays the status in the system tray and provides complete autonomy without an Internet connection.

---

## 📦 Features
- Voice text input via microphone
- Local speech recognition (without internet connection)
- Support for hotkeys to start and stop recording (`Ctrl + F4`)
- Recording status indication in the tray
- Sound notification about the start and end of recording
- Work in the background

---

## 🚀 Installation and launch
Deploy the environment (Python 3.9)
```bash
py -3.9 -m venv venv
venv/scripts/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Build `stt.exe`
```bash
pyinstaller --onefile --noconsole main.py -n stt.exe
```

`stt.exe` will be built in the `dist/` directory, where the files are already located models, notification sounds and the `whisper.cpp` binary.

Then the `dist/` directory can be copied to any convenient location on the computer and a shortcut to `cpp.exe` can be created in the startup folder to run with Windows startup.

---

## ▶ Usage
1. Run `stt.exe`
2. The icon will appear in the tray
3. Press `Ctrl + F4` to start/stop recording
4. The recognized text will be automatically entered into the active window

---

## 🔊 Sound notifications
The notification signal can be replaced by replacing the `dist/notice.mp3` file, provided that the name is preserved.

---
[LICENSE](LICENSE)
