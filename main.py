import os
from gtts import gTTS
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip

def create_short(text, bg_video_path, output_name):
    # 1. Generate AI Voiceover
    tts = gTTS(text=text, lang='en', tld='us')
    tts.save("voiceover.mp3")
    
    # 2. Load audio and background video
    audio = AudioFileClip("voiceover.mp3")
    video = VideoFileClip(bg_video_path).subclip(0, audio.duration)
    
    # 3. Add simple overlay text
    txt_clip = TextClip(text, fontsize=50, color='white', bg_color='black', method='caption', size=video.size)
    txt_clip = txt_clip.set_pos('center').set_duration(audio.duration)
    
    # 4. Stitch audio and video together
    final_video = CompositeVideoClip([video, txt_clip])
    final_video = final_video.set_audio(audio)
    final_video.write_videofile(output_name, fps=24, codec="libx264")

if __name__ == "__main__":
    story_text = "Here is a crazy Reddit story about how I built an automated video tool."
    create_short(story_text, "gameplay.mp4", "viral_short.mp4")
  
