import sounddevice as sd
import soundfile as sf
import warnings
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")
import whisper
from pydub import AudioSegment, effects, silence
import threading
import queue
import os
import time
import datetime
import tkinter as tk

CHUNK_DURATION_SEC = 60  # 1 minute per chunk
SAMPLERATE = 16000
CHANNELS = 1
MODEL_NAME = "base"

# Generate a unique transcript filename in the format 17JUN2025_1530.txt
now = datetime.datetime.now()
TRANSCRIPT_FILE = now.strftime("%d%b%Y_%H%M.txt").upper()

def preprocess_audio(input_wav, output_wav, silence_thresh=-40, min_silence_len=2000):
    audio = AudioSegment.from_wav(input_wav)
    normalized = effects.normalize(audio)
    chunks = silence.split_on_silence(normalized,
                                      min_silence_len=min_silence_len,
                                      silence_thresh=silence_thresh,
                                      keep_silence=250)
    processed_audio = AudioSegment.empty()
    for chunk in chunks:
        processed_audio += chunk
    processed_audio.export(output_wav, format="wav")
    return output_wav

def transcribe_and_append(chunk_wav, transcript_file, model):
    clean_wav = chunk_wav.replace(".wav", "_clean.wav")
    preprocess_audio(chunk_wav, clean_wav)
    result = model.transcribe(clean_wav, language="en", task="transcribe", temperature=0)
    with open(transcript_file, "a", encoding="utf-8") as f:
        f.write(result["text"] + "\n")
    os.remove(chunk_wav)
    os.remove(clean_wav)

def recorder_worker(audio_q, stop_event, status):
    chunk_idx = 1
    while not stop_event.is_set():
        if not status["recording"]:
            time.sleep(0.5)
            continue
        chunk_filename = f"meeting_chunk{chunk_idx}.wav"
        print(f"Recording chunk {chunk_idx}...")
        with sf.SoundFile(chunk_filename, mode='w', samplerate=SAMPLERATE, channels=CHANNELS) as file:
            with sd.InputStream(samplerate=SAMPLERATE, channels=CHANNELS, dtype='float32') as stream:
                frames = int(SAMPLERATE * CHUNK_DURATION_SEC)
                data, _ = stream.read(frames)
                file.write(data)
        audio_q.put(chunk_filename)
        chunk_idx += 1

def transcriber_worker(audio_q, stop_event, model):
    while not (stop_event.is_set() and audio_q.empty()):
        try:
            chunk_wav = audio_q.get(timeout=1)
            print(f"Transcribing {chunk_wav}...")
            transcribe_and_append(chunk_wav, TRANSCRIPT_FILE, model)
            audio_q.task_done()
        except queue.Empty:
            continue

if __name__ == "__main__":
    audio_q = queue.Queue()
    stop_event = threading.Event()
    model = whisper.load_model(MODEL_NAME)
    status = {"recording": False}

    recorder_thread = threading.Thread(target=recorder_worker, args=(audio_q, stop_event, status), daemon=True)
    transcriber_thread = threading.Thread(target=transcriber_worker, args=(audio_q, stop_event, model), daemon=True)
    recorder_thread.start()
    transcriber_thread.start()

    # Tkinter GUI
    def start_recording_gui():
        if not status["recording"]:
            status["recording"] = True
            print("Recording started.")
            status_label.config(text="Status: Recording", fg="green")

    def stop_recording_gui():
        if status["recording"]:
            status["recording"] = False
            print("Recording stopped.")
            status_label.config(text="Status: Idle", fg="red")

    def on_close():
        stop_recording_gui()
        stop_event.set()
        root.destroy()

    root = tk.Tk()
    root.title("Meeting Transcriber")
    root.geometry("260x140")
    root.resizable(False, False)
    root.attributes("-topmost", True)

    status_label = tk.Label(root, text="Status: Idle", fg="red", font=("Arial", 12))
    status_label.pack(pady=10)

    start_btn = tk.Button(root, text="Start Recording", command=start_recording_gui, width=20)
    start_btn.pack(pady=5)
    stop_btn = tk.Button(root, text="Stop Recording", command=stop_recording_gui, width=20)
    stop_btn.pack(pady=5)

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()

    # Wait for threads to finish
    stop_event.set()
    recorder_thread.join(timeout=2)
    audio_q.join(timeout=2)
    transcriber_thread.join(timeout=2)
    print(f"Transcript saved to {TRANSCRIPT_FILE}")