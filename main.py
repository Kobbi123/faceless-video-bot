import os
import re
import random
import requests
from gtts import gTTS
from moviepy import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip

class AutoShortsEngine:
    def __init__(self, bg_video_path="gameplay.mp4", output_path="viral_short.mp4"):
        self.bg_video_path = bg_video_path
        self.output_path = output_path
        self.audio_path = "voiceover.mp3"

    def fetch_reddit_story(self, subreddit="AskReddit"):
        """Scrapes trending stories with a robust header."""
        print(f"🔍 Fetching viral story from r/{subreddit}...")
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=15"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                posts = response.json()['data']['children']
                for post in posts:
                    p = post['data']
                    title = p.get('title', '')
                    body = p.get('selftext', '')
                    full_text = f"{title}. {body}".strip()
                    
                    # Ideal length for a 30-45s Short
                    if 150 <= len(full_text) <= 450 and not p.get('over_18', False):
                        clean_text = re.sub(r'http\S+|[^\w\s.,!\?]', '', full_text)
                        print(f"✅ Story Found: {title[:50]}...")
                        return clean_text
        except Exception as e:
            print(f"⚠️ Reddit Fetch Warning: {e}")

        # High-converting default viral hook if API is throttled
        return ("What is a dark secret about the gaming industry that most people have no idea about? "
                "Developers regularly leave cut content hidden deep within game files, "
                "and sometimes whole unreleased levels stay buried for over two decades.")

    def generate_audio(self, text):
        """Generates clear narration audio."""
        print("🎙️ Generating AI Voiceover...")
        tts = gTTS(text=text, lang='en', tld='us')
        tts.save(self.audio_path)
        return AudioFileClip(self.audio_path)

    def create_caption_clips(self, text, audio_duration, video_width):
        """Generates properly chunked 2-3 word animated subtitle phrases."""
        words = text.split()
        if not words:
            return []

        # Group words into 2-3 word chunks so text never gets clipped off-screen
        chunks = []
        curr_chunk = []
        for word in words:
            curr_chunk.append(word)
            if len(curr_chunk) >= 2 or len(word) > 7:
                chunks.append(" ".join(curr_chunk))
                curr_chunk = []
        if curr_chunk:
            chunks.append(" ".join(curr_chunk))

        chunk_duration = audio_duration / len(chunks)
        text_clips = []

        for i, chunk in enumerate(chunks):
            start_time = i * chunk_duration
            
            # Highlight keyword colors dynamically
            text_color = 'yellow' if i % 2 == 0 else 'cyan'
            
            txt_clip = (TextClip(
                            text=chunk.upper(), 
                            font_size=55, 
                            color=text_color, 
                            stroke_color='black', 
                            stroke_width=4,
                            method='caption',
                            size=(video_width - 120, None)
                        )
                        .with_position(('center', 0.45), relative=True)
                        .with_start(start_time)
                        .with_duration(chunk_duration))
            
            text_clips.append(txt_clip)

        return text_clips

    def render(self, subreddit="AskReddit"):
        """Assembles and renders the full short."""
        script = self.fetch_reddit_story(subreddit)
        
        audio = self.generate_audio(script)
        full_bg = VideoFileClip(self.bg_video_path)
        
        if full_bg.duration < audio.duration:
            bg_video = full_bg.loop(duration=audio.duration)
        else:
            max_start = max(0, full_bg.duration - audio.duration - 1)
            start_point = random.uniform(0, max_start) if max_start > 0 else 0
            bg_video = full_bg.subclipped(start_point, start_point + audio.duration)

        caption_clips = self.create_caption_clips(script, audio.duration, bg_video.w)

        print("🎬 Rendering Final Video Output...")
        final_video = CompositeVideoClip([bg_video] + caption_clips)
        final_video = final_video.with_audio(audio)
        
        final_video.write_videofile(
            self.output_path, 
            fps=24, 
            codec="libx264", 
            audio_codec="aac",
            preset="ultrafast"
        )
        print("🎉 Video Generation Complete!")

if __name__ == "__main__":
    engine = AutoShortsEngine()
    engine.render(subreddit="AskReddit")
