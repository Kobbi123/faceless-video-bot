import os
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from gtts import gTTS
from moviepy.editor import TextClip, CompositeVideoClip, AudioFileClip, ColorClip

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Fixes cross-origin connection issue

OUTPUT_DIR = "generated_videos"
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "AutoShorts Backend Engine is Live!"})

@app.route('/generate-short', methods=['POST'])
def generate_short():
    try:
        data = request.get_json() or {}
        prompt = data.get('prompt', 'Mind blowing fact about space.')

        # 1. Generate Audio via gTTS
        audio_filename = "speech.mp3"
        audio_path = os.path.join(OUTPUT_DIR, audio_filename)
        tts = gTTS(text=prompt, lang='en', slow=False)
        tts.save(audio_path)

        # 2. Setup Audio Clip & Duration
        audio_clip = AudioFileClip(audio_path)
        duration = audio_clip.duration

        # 3. Create Vertical Background (9:16 aspect ratio)
        bg_clip = ColorClip(size=(720, 1280), color=(15, 23, 42), duration=duration)

        # 4. Burn Text/Captions
        txt_clip = TextClip(
            prompt,
            fontsize=40,
            color='yellow',
            font='Helvetica-Bold',
            method='caption',
            size=(620, None)
        ).set_position('center').set_duration(duration)

        # 5. Composite Video & Add Audio
        final_video = CompositeVideoClip([bg_clip, txt_clip]).set_audio(audio_clip)

        output_filename = "output_short.mp4"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        final_video.write_videofile(
            output_path,
            fps=24,
            codec='libx264',
            audio_codec='aac',
            verbose=False,
            logger=None
        )

        # Clean up audio resource
        audio_clip.close()

        return jsonify({
            "status": "success",
            "video_url": f"/download/{output_filename}"
        })

    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(OUTPUT_DIR, filename)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
