import sys
import sounddevice as sd
import wave
import queue
import tempfile
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw
import threading
import os
import subprocess
import re

from playsound import playsound

def play_notification(sound_file):
    threading.Thread(target=playsound, args=(sound_file,), daemon=True).start()


WHISPER_PATH = 'main.exe'
MODEL_PATH = 'base.bin'

def create_icon(color):
        image = Image.new('RGB', (64, 64), 'white')
        draw = ImageDraw.Draw(image)
        fill = 'red' if color == 'recording' else 'gray'
        draw.ellipse((16, 16, 48, 48), fill=fill)
        return image


icon = None
recording = False

samplerate = 16000
channels = 1
recording = False
audio_q = queue.Queue()
stream = None


def start_hotkey_listener(icon_ref):
    from pynput import keyboard

    def on_activate():
        toggle_recording(icon_ref)

    with keyboard.GlobalHotKeys({
        '<ctrl>+<f4>': on_activate
    }) as h:
        h.join()


def toggle_recording(icon_obj=None):
    global recording, icon
    recording = not recording
    
    if recording:
        if icon: icon.icon = create_icon('recording')
        play_notification("notice.mp3")
        # print("🎙 Запись началась")
        threading.Thread(target=start_recording).start()
    else:
        if icon: icon.icon = create_icon('idle')
        play_notification("notice.mp3")
        # print("🛑 Запись остановлена")
        threading.Thread(target=stop_recording_and_process).start()



def start_recording():
    global stream
    
    def audio_callback(indata, frames, time, status):
        audio_q.put(indata.copy())
    
    audio_q.queue.clear()
    stream = sd.InputStream(samplerate=samplerate, channels=channels, dtype='int16', callback=audio_callback)
    stream.start()
    # print("🎙 Запись начата")


def stop_recording_and_process():
    global stream
    # print("🛑 Остановка записи")
    if stream:
        stream.stop()
        stream.close()
        stream = None

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        path = f.name

    with wave.open(path, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)
        wf.setframerate(samplerate)
        while not audio_q.empty():
            wf.writeframes(audio_q.get())

    # print(f"💾 Записано в файл: {path}")
    text = transcribe(path)
    if text:
        type_text(text)
        os.remove(path)
        os.remove(path + '.txt')
        

def type_text(text):
    from pynput.keyboard import Controller
    kb = Controller()
    for ch in text:
        kb.type(ch)

# Распознавание через whisper.cpp
def transcribe(filename):
    cmd = [WHISPER_PATH, '-m', MODEL_PATH, '-f', filename, '-otxt', '-l', 'ru']
    creationflags = 0
    if sys.platform == "win32":
        creationflags = subprocess.CREATE_NO_WINDOW
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=creationflags)
    txt_file = filename + '.txt'
    if os.path.exists(txt_file):
        with open(txt_file, 'r', encoding='utf-8') as f:
            text = re.sub(r"\[.*\]", "", f.read().strip()) 
            # print(f"📝 Распознано: {text}")
            return text
    return ""


def setup_tray():
    global icon
    icon = Icon("Whisper", icon=create_icon('idle'), menu=Menu(
        MenuItem("🎙 Переключить запись", lambda i, _: toggle_recording(i)),
        MenuItem("❌ Выход", lambda i, _: i.stop())
    ))
    threading.Thread(target=start_hotkey_listener, args=(icon,), daemon=True).start()
    icon.run()


setup_tray()