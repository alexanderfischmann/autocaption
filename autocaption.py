import tkinter as tk
from tkinter import filedialog, messagebox
import whisper
import threading
import os

def format_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    milliseconds = int((seconds % 1) * 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

def transcribe_video(video_path):
    try:
        model = whisper.load_model("medium")  # You can change to 'base', 'small', etc.
        result = model.transcribe(video_path, fp16=False)

        srt_path = os.path.splitext(video_path)[0] + ".srt"
        with open(srt_path, "w", encoding="utf-8") as f:
            for i, segment in enumerate(result["segments"], 1):
                start = format_timestamp(segment["start"])
                end = format_timestamp(segment["end"])
                f.write(f"{i}\n{start} --> {end}\n{segment['text'].strip()}\n\n")

        messagebox.showinfo("Success", f"Subtitles saved:\n{srt_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to transcribe:\n{str(e)}")

def choose_file():
    file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.mov *.mkv *.avi")])
    if file_path:
        status_label.config(text="Transcribing...")
        threading.Thread(target=lambda: transcribe_video_with_ui(file_path)).start()

def transcribe_video_with_ui(path):
    transcribe_video(path)
    status_label.config(text="Done. Choose another file if you like.")

# GUI setup
root = tk.Tk()
root.title("AutoCaption - Whisper Subtitle Generator")
root.geometry("400x200")

tk.Label(root, text="Select a video to auto-generate subtitles:").pack(pady=20)
tk.Button(root, text="Choose Video", command=choose_file, width=20, height=2).pack()
status_label = tk.Label(root, text="")
status_label.pack(pady=20)

root.mainloop()