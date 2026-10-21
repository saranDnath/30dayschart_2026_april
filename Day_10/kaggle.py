# %% [code]
# Install libraries which are not in Kaggle
import os
os.system("pip install deep-translator word2number")

# load the libraries 

import os
import requests
import pandas as pd
import re
import math
from deep_translator import GoogleTranslator
from word2number import w2n
from dotenv import load_dotenv
from datetime import datetime

# function for parsing duration

def parse_duration(pt_str):
    if not pt_str:
        return '00:00'
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', pt_str)
    if not match:
        return pt_str
    h = int(match.group(1) or 0)
    m = int(match.group(2) or 0)
    s = int(match.group(3) or 0)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


# 1. Credentials
from kaggle_secrets import UserSecretsClient
user_secrets = UserSecretsClient()
API_KEY = user_secrets.get_secret("YOUTUBE_API_KEY")

PLAYLIST_ID = "UUIB65_E_7XEScU2NB135wDw"  # Coke Studio Bangla Uploads
BASE_URL = "https://www.googleapis.com/youtube/v3/playlistItems"

print("Fetching video IDs via pagination loop...")

# 2. The Pagination Loop: Getting ALL videos
video_ids = []
next_page_token = None

while True:
    query_params = {
        'part': 'contentDetails',
        'playlistId': PLAYLIST_ID,
        'maxResults': 50,
        'key': API_KEY
    }
    
    if next_page_token:
        query_params['pageToken'] = next_page_token
        
    response = requests.get(BASE_URL, params=query_params).json()
    
    # Extract IDs and append to our master list
    for item in response.get('items', []):
        video_ids.append(item['contentDetails']['videoId'])
        
    next_page_token = response.get('nextPageToken')
    
    # Break the loop if there are no more pages
    if not next_page_token:
        break

print(f"Found {len(video_ids)} total videos. Fetching statistics in batches...")

# 3. Fetch Statistics in Batches of 50 and Categorize Dynamically
stats_url = "https://www.googleapis.com/youtube/v3/videos"
video_data = []

# Loop through our IDs in chunks of 50
for i in range(0, len(video_ids), 50):
    chunk = video_ids[i:i+50]
    
    stats_params = {
        'part': 'statistics,snippet,contentDetails',
        'id': ','.join(chunk),  # Joins up to 50 IDs with commas
        'key': API_KEY
    }
    
    stats_response = requests.get(stats_url, params=stats_params).json()
    
    for item in stats_response.get('items', []):
        title = item['snippet']['title']
        description = item['snippet'].get('description', '')
        text_for_search = title + " " + description

        m = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', item['contentDetails'].get('duration', ''))
        duration_secs = (int(m.group(1) or 0) * 3600 + int(m.group(2) or 0) * 60
                         + int(m.group(3) or 0)) if m else 0

        
        # A. Translate Title by google translate
        try:
            eng_title = GoogleTranslator(source='auto', target='en').translate(title)
        except Exception:
            eng_title = title  # Fallback to original if translation fails
            
        # B. Parse Description Metadata 
        spotify_link = None
        spotify_match = re.search(r'(?i)(?:Listen on Spotify|Spotify):\s*(https://open\.spotify\.com/[^\s]+)', description)
        if spotify_match:
            spotify_link = spotify_match.group(1)
            
        director = None
        # Line must START with "Director:" (skips "Assoc Creative Director:" etc.)
        # and the name must stay on that line (no \s, which would swallow the next line)
        director_match = re.search(r'(?im)^\s*Director:\s*([A-Za-z .]+)', description)
        if director_match:
            director = director_match.group(1).strip()
            
        vocals = []
        for line in description.split('\n'):
            line = line.strip()
            if not line or 'engineer' in line.lower() or 'arrangement' in line.lower():
                continue
            # Lead vocals only — skip backing singers / choir
            if re.search(r'(?i)backing|choir|chorus', line):
                continue
            # Handle both formats: "Artist: Vocals" (S2/S3) and "Artist - Vocals" (S1)
            if 'vocal' in line.lower():
                # Colon format: e.g. "Vocals: Arnob" or "Lead Vocals: Arnob"
                if ':' in line:
                    parts = line.split(':', 1)
                    left, right = parts[0].strip(), parts[1].strip()
                    artist = right if 'vocal' in left.lower() else left
                # Dash format: e.g. "Arnob - Vocals" or "Arnob - Lead Vocals"
                elif ' - ' in line:
                    parts = line.split(' - ', 1)
                    left, right = parts[0].strip(), parts[1].strip()
                    artist = left if 'vocal' in right.lower() else right
                else:
                    continue
                artist = re.sub(r'\(.*?\)', '', artist).strip()  # Clean up brackets
                # Skip lines that are clearly not artist names (too long or contain symbols)
                if artist and len(artist) < 60 and not re.search(r'[/@#]', artist):
                    vocals.append(artist)
        vocals_str = ', '.join(vocals) if vocals else None

        # C. Prioritized Video Type
        # Hashtags (#Shorts / #Reels, even glued like "#ReelsSong") count anywhere,
        # but the plain word only counts in the TITLE — descriptions contain credits
        # like "VIDEO PRODUCTION: INDIE REELS" that are not reels.
        is_shorts = re.search(r'(?i)#shorts', text_for_search) or re.search(r'(?i)\bshorts\b', title)
        is_reels = re.search(r'(?i)#reels', text_for_search) or re.search(r'(?i)\breels?\b', title)
        # \b = whole words only, so e.g. "BTS" can't match inside another word
        is_bts = re.search(r'(?i)Behind The Magic|\bBTS\b|\bMaking\b|Set Design', title)
        is_milestone = re.search(r'(?i)\bmillion\b|views?-এ|ফেলেছে|অভিনন্দন|congratulat', title)
        is_live = re.search(r'(?i)\blive\b|লাইভ', title)
        is_promo = re.search(r'(?i)\bTeaser\b|\bPromo\b|\bTrailer\b|\bAnnouncement\b|আসছে', title)
        
        if is_shorts:
            video_type = "Shorts"
        elif is_reels:
            video_type = "Reels"
        elif is_bts:
            video_type = "Behind the Scenes"
        elif is_milestone:
            video_type = "Celebration / Milestone"
        elif is_live:
            video_type = "Live Event"
        elif is_promo:
            video_type = "Promo / Teaser"
        elif duration_secs <= 90:
            # Untagged vertical clips (16-sec snippets, 01:01 song stories) — not full songs.
            # Shortest real music video is ~3:48, so 90s is a safe cut-off.
            video_type = "Shorts"
        elif spotify_link or vocals_str:
            video_type = "Official Music Video"
        else:
            video_type = "Uncategorized"

        # F. Genre Detection (only for Official Music Videos)
        # Whole-word regexes (\b): plain substrings matched names/credits before,
        # e.g. 'sari' in "Ansari", 'rap' in "Photography", 'blues' in "Blues Production".
        GENRE_PATTERNS = {
            'Folk': r'\bfolk\b|\bbaul\b|\bbhatiali\b|\bbhawaiya\b|\bhajong\b|\blalon\b|\bmarfati\b|\bjari\b|\bsari gaan\b|\bkirtan\b',
            'Qawwali': r'\bqaw+ali\b|\bqalandar\b|\bsufi\b',
            'Rock': r'\brock\b|\bmetal\b',
            'Pop': r'\bpop\b',
            'Classical': r'\bclassical\b|\braa?ga?\b|\bthumri\b|\bkheyal\b|\bkhayal\b|\bgharana\b',
            'Fusion': r'\bfusion\b',
            'Latin': r'\blatin\b|\bbossa nova\b|\bsamba\b',
            'Jazz': r'\bjazz\w*\b',
            'R&B / Soul': r'\br&b\b|\bsoul music\b|\bneo-soul\b|\bblues\b',
            'Hip-Hop': r'\bhip[- ]?hop\b|\brap\b|\brapper\b|\brapping\b',
            'Afrobeat': r'\bafrobeats?\b',
        }
        if video_type == "Official Music Video":
            # Search only the song's story paragraphs, not the credits list.
            # Credits are short lines and/or "Role: Name" lines.
            story_text = '\n'.join(
                line.strip() for line in description.split('\n')
                if len(line.strip()) >= 80 and ':' not in line.strip()[:40]
            )
            detected_genres = []
            for genre, pattern in GENRE_PATTERNS.items():
                if re.search(pattern, story_text, re.IGNORECASE):
                    detected_genres.append(genre)
            # Default to Fusion for CSB since it's always cross-genre
            if not detected_genres:
                detected_genres = ['Fusion']
            genre_str = ', '.join(detected_genres)
        else:
            genre_str = "Not Applicable"
        
        # D. Extract the Season dynamically
        season_match = re.search(r'(?i)(?:CokeStudioBanglaSeason|CokeStudioBanglaS|CSB S|Season)\s*(\d+|one|two|three|four|five|six|seven|eight|nine|ten)\b', text_for_search)
        season = "Uncategorized"
        if season_match:
            season_val = season_match.group(1).lower()
            try:
                season_num = w2n.word_to_num(season_val)
                season = f"Season {season_num}"
            except ValueError:
                season = f"Season {season_val.title()}"

        # Clean Missing Values
        vocals_str = vocals_str if vocals_str else "Not Applicable"
        spotify_link = spotify_link if spotify_link else "Not Applicable"
        director = director if director else "Not Applicable"
        
        # E. Fetch Thumbnails & Metadata
        thumbnails = item['snippet'].get('thumbnails', {})
        thumbnail_url = None
        if 'maxres' in thumbnails:
            thumbnail_url = thumbnails['maxres'].get('url')
        elif 'high' in thumbnails:
            thumbnail_url = thumbnails['high'].get('url')
        elif 'standard' in thumbnails:
            thumbnail_url = thumbnails['standard'].get('url')
        elif 'medium' in thumbnails:
            thumbnail_url = thumbnails['medium'].get('url')
        elif 'default' in thumbnails:
            thumbnail_url = thumbnails['default'].get('url')
            
        video_url = f"https://www.youtube.com/watch?v={item['id']}"
        duration_raw = item['contentDetails'].get('duration', '')
        duration_fmt = parse_duration(duration_raw)
        last_updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        video_data.append({
            'Video_ID': item['id'],
            'Video_URL': video_url,
            'Title': title,
            'English_Title': eng_title,
            'Published_At': pd.to_datetime(item['snippet']['publishedAt']).strftime('%Y-%m-%d'),
            'Video_Duration': duration_fmt,
            'Views': int(item['statistics'].get('viewCount', 0)),
            'Likes': int(item['statistics'].get('likeCount', 0)),
            'Comments': int(item['statistics'].get('commentCount', 0)),
            'Video_Type': video_type,
            'Season': season,
            'Lead_Vocals': vocals_str,
            'Spotify_Link': spotify_link,
            'Director': director,
            'Thumbnail_URL': thumbnail_url,
            'Genre': genre_str,
            'Last_Updated': last_updated,
            'Video_Details': description
        })

# 4. Save to local directory
df = pd.DataFrame(video_data)
output_path = "coke_studio_bangla_raw.csv"

try:
    df.to_csv(output_path, index=False)
    print(f"Success! Dataset saved to: {output_path}")
except PermissionError:
    import time
    fallback_path = f"coke_studio_bangla_raw_{int(time.time())}.csv"
    df.to_csv(fallback_path, index=False)
    print(f"\n PermissionError: '{output_path}' was open and locked.")
    print(f"Success! Dataset was safely saved instead to: {fallback_path}")