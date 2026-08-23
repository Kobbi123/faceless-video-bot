import os
import requests
from gtts import gTTS
from moviepy import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip

def get_reddit_story(subreddit="gaming"):
    # Fetch top daily post from specified subreddit
    headers = {'User-Agent': 'Mozilla/5.0'}
    url = f"https://www.reddit.com/r/{subreddit}/top.json?limit=5&t=day"
    response = requests.get(url, headers=headers).json()
    
    posts = response['data']['children']
    for post in posts:
        data = post['data']
        # Grab text post that isn't too long or short
        story_text = f"{data['title']}. {data.get('selftext', '')}"
        if 50 < len(story_text) < 400:
            return data['title'], story_text[:300]
            
    return "Trending Gaming News", "Here is a quick look at what is happening in the gaming world today."

def create_reddit_short(subreddit, bg_video_path, output_name):
    # 1. Fetch live Reddit post
    title, story_text = get_reddit_story(subreddit)
    print(f"Fetched Story: {title}")
    
    # 2. Generate Voiceover
    tts = gTTS(text=story_text, lang='en', tld='us')
    tts.save("voiceover.mp3")
    
    audio = AudioFileClip("voiceover.mp3")
    video = VideoFileClip(bg_video_path).subclipped(0, audio.duration)
    
    # 3. Dynamic Subtitles
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
    
    # 4. Render Final Video
    final_video = CompositeVideoClip([video] + text_clips)
    final_video = final_video.with_audio(audio)
    final_video.write_videofile(output_name, fps=24, codec="libx264", audio_codec="aac")

if __name__ == "__main__":
    # Change 'gaming' to 'AskReddit' or 'AITAH' anytime!
    create_reddit_short("gaming", "gameplay.mp4", "viral_short.mp4")
    
