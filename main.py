import os
from gtts import gTTS
from moviepy import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip

def create_viral_short(text, bg_video_path, output_name):
    # 1. Generate Voiceover
    tts = gTTS(text=text, lang='en', tld='us')
    tts.save("voiceover.mp3")
    
    audio = AudioFileClip("voiceover.mp3")
    video = VideoFileClip(bg_video_path).subclipped(0, audio.duration)
    
    # 2. Word-by-Word Caption Generator
    words = text.split()
    word_duration = audio.duration / len(words)
    
    text_clips = []
    for i, word in enumerate(words):
        start_time = i * word_duration
        
        # Clean modern text without the black box background
        txt_clip = (TextClip(
                        text=word.upper(), 
                        font_size=65, 
                        color='yellow', 
                        stroke_color='black', 
                        stroke_width=3,
                        method='caption',
                        size=(video.w - 80, None)
                    )
                    .with_position(('center', 'center'))
                    .with_start(start_time)
                    .with_duration(word_duration))
        
        text_clips.append(txt_clip)
    
    # 3. Composite Video with Subtitles
    final_video = CompositeVideoClip([video] + text_clips)
    final_video = final_video.with_audio(audio)
    
    # 4. Export Video
    final_video.write_videofile(output_name, fps=24, codec="libx264", audio_codec="aac")

if __name__ == "__main__":
    story_text = "Here is a crazy story about how I built an automated video tool."
    create_viral_short(story_text, "gameplay.mp4", "viral_short.mp4")
    
