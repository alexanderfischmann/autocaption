from flask import Flask, request, send_file, render_template
import whisper
import os
import tempfile

app = Flask(__name__)
model = whisper.load_model("base")  # You can change this to "medium" or "large"

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/upload', methods=['POST'])
def upload():
    if 'video' not in request.files:
        return "No file uploaded", 400

    video_file = request.files['video']
    if video_file.filename == '':
        return "Empty filename", 400

    # Save uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(video_file.filename)[1]) as temp_video:
        video_path = temp_video.name
        video_file.save(video_path)

    # Transcribe and convert to SRT
    try:
        result = model.transcribe(video_path, fp16=False)
        srt_path = video_path + ".srt"

        with open(srt_path, "w", encoding="utf-8") as f:
            for i, segment in enumerate(result["segments"], start=1):
                start = format_timestamp(segment["start"])
                end = format_timestamp(segment["end"])
                text = segment["text"].strip()
                f.write(f"{i}\n{start} --> {end}\n{text}\n\n")

        return send_file(srt_path, as_attachment=True, download_name=video_file.filename.rsplit('.', 1)[0] + '.srt')
    finally:
        # Clean up temporary files
        os.remove(video_path)
        if os.path.exists(srt_path):
            os.remove(srt_path)

def format_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

if __name__ == '__main__':
    app.run(debug=True)
