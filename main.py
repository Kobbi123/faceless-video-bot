import os
import requests
from gtts import gTTS
from moviepy import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip

def get_reddit_story(subreddit="AskReddit"):
    try:
        # Realistic User-Agent header to bypass Reddit bot checks
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=10"
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            posts = data['data']['children']
            for post in posts:
                post_data = post['data']
                text = post_data.get('selftext', '')
                title = post_data.get('title', '')
                full_story = f"{title}. {text}"
                
                # Ensure story is the right length for a short
                if 80 < len(full_story) < 350:
                    return title, full_story[:300]
    except Exception as e:
        print(f"Reddit fetch fallback triggered: {e}")
        
    # Safe fallback story if Reddit blocks connection
    return "Gaming Secret", "Did you know that video game developers often hide secret messages inside the code that only reveal themselves after years of searching?"

def create_reddit_short(subreddit, bg_video_path, output_name):
    title, story_text = get_reddit_story(subreddit)
    print(f"Using Story: {story_text}")
    
    # 1. Voiceover
    tts = gTTS(text=story_text, lang='en', tld='us')
    tts.save("voiceover.mp3")
    
    audio = AudioFileClip("voiceover.mp3")
    video = VideoFileClip(bg_video_path).subclipped(0, audio.duration)
    
    # 2. Single-Word Subtitles
    words = story_text.split()
    word_duration = audio.duration / len(words)
    
    text_clips = []
    for i, word in enumerate(words):
        start_time = i * word_duration
        
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
    
    # 3. Composite Video
    final_video = CompositeVideoClip([video] + text_clips)
    final_video = final_video.with_audio(audio)
    final_video.write_videofile(output_name, fps=24, codec="libx264", audio_codec="aac")

if __name__ == "__main__":
    create_reddit_short("AskReddit", "gameplay.mp4", "viral_short.mp4")
    
