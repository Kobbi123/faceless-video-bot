import os
import random
import requests
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from gtts import gTTS
from moviepy import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip

app = Flask(__name__)
CORS(app)  # Allows your frontend UI to talk to this backend

os.makedirs("exports", exist_ok=True)

def generate_script(prompt):
    if len(prompt.split()) > 15:
        return prompt
    templates = [
        f"Here is a crazy secret about {prompt} that almost nobody knows. Developers hide hidden easter eggs deep inside the source code.",
        f"Did you ever wonder why {prompt} is so popular? Psychology plays a massive role in keeping people hooked."
    ]
    return random.choice(templates)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "running"}), 200

@app.route('/generate-short', methods=['POST'])
def create_short():
    data = request.json or {}
    user_prompt = data.get("prompt", "gaming secrets")
    
    script_text = generate_script(user_prompt)
    
    # 1. Voiceover
    audio_path = "temp_voice.mp3"
    tts = gTTS(text=script_text, lang='en', tld='us')
    tts.save(audio_path)
    audio = AudioFileClip(audio_path)
    
    # 2. Gameplay Video
    bg_video_path = "gameplay.mp4"
    if not os.path.exists(bg_video_path):
        return jsonify({"error": "gameplay.mp4 file missing on server"}), 500
        
    full_bg = VideoFileClip(bg_video_path)
    bg_video = full_bg.loop(duration=audio.duration) if full_bg.duration < audio.duration else full_bg.subclipped(0, audio.duration)
    
    # 3. Dynamic Subtitles
    words = script_text.split()
    chunks = []
    curr = []
    for w in words:
        curr.append(w)
        if len(curr) >= 2:
            chunks.append(" ".join(curr))
            curr = []
    if curr:
        chunks.append(" ".join(curr))

    chunk_dur = audio.duration / len(chunks)
    text_clips = []
    for i, chunk in enumerate(chunks):
        txt = (TextClip(
                    text=chunk.upper(),
                    font_size=55,
                    color='yellow' if i % 2 == 0 else 'cyan',
                    stroke_color='black',
                    stroke_width=4,
                    method='caption',
                    size=(bg_video.w - 100, None)
                )
                .with_position(('center', 0.45), relative=True)
                .with_start(i * chunk_dur)
                .with_duration(chunk_dur))
        text_clips.append(txt)

    # 4. Render
    final_video = CompositeVideoClip([bg_video] + text_clips).with_audio(audio)
    out_name = f"short_{random.randint(1000,9999)}.mp4"
    out_path = os.path.join("exports", out_name)
    final_video.write_videofile(out_path, fps=24, codec="libx264", audio_codec="aac", preset="ultrafast")
    
    return jsonify({
        "status": "success",
        "script": script_text,
        "video_url": f"/download/{out_name}"
    })

@app.route('/download/<filename>', methods=['GET'])
def download(filename):
    return send_file(os.path.join("exports", filename), as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
