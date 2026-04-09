import json
import subprocess
import urllib.request
import urllib.parse
import os
import base64
import glob
import shutil
import re
import time

def format_timestamp(ms):
    """Precise rounding to HH:MM:SS.mmm."""
    seconds, milliseconds = divmod(ms, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}.{int(milliseconds):03}"

def get_mediainfo_data(filepath):
    cmd = ["mediainfo", "--Output=JSON", filepath]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout).get("media", {}).get("track", [])
    except Exception as e:
        print(f"    [!] Error running mediainfo: {e}")
        return []

def is_generic_chapters(tracks):
    menu_track = next((t for t in tracks if t.get("@type") == "Menu"), None)
    if not menu_track: return True 
    extra = menu_track.get("extra", {})
    chapter_titles = [str(v) for k, v in extra.items() if ":" in k]
    if len(chapter_titles) <= 1: return True
    generic_patterns = [r"^chapter\s*\d+$", r"^\d+$", r"^part\s*\d+$"]
    for title in chapter_titles[:3]:
        clean_title = title.strip().lower()
        if not any(re.match(p, clean_title) for p in generic_patterns):
            return False 
    return True

def process_file(filepath):
    print(f"\n{'='*40}\n>>> FILE: {os.path.basename(filepath)}")
    all_tracks = get_mediainfo_data(filepath)
    if not all_tracks: return
    
    general_track = next((t for t in all_tracks if t.get("@type") == "General"), {})
    extra_tags = general_track.get("extra", {})
    
    # 1. THE ASIN GATEKEEPER
    asin = general_track.get("CDEK") or extra_tags.get("CDEK")
    if not asin:
        print("    [SKIP] No CDEK/ASIN tag found. Skipping processing and movement.")
        return

    # Metadata Extraction
    author = general_track.get("Performer") or general_track.get("Artist") or "Unknown Author"
    album = general_track.get("Album") or general_track.get("Title") or "Unknown Album"
    year = str(general_track.get("Recorded_Date") or general_track.get("Released_Date") or "0000")[:4]
    series = extra_tags.get("series") or "Non-Series"

    print(f"    [INFO] ASIN Detected: {asin}")
    print(f"    [INFO] Meta: {author} | {album} ({year})")

    # Chapter Retrieval
    chapters = None
    json_val = extra_tags.get("JSON") or general_track.get("JSON")
    
    # Check embedded JSON first (if it has multiple chapters)
    if json_val:
        try:
            try:
                decoded = base64.b64decode(json_val).decode('utf-8')
                json_data = json.loads(decoded)
            except:
                json_data = json.loads(json_val)
            
            temp_chapters = json_data.get("chapters")
            if temp_chapters and len(temp_chapters) > 1:
                chapters = temp_chapters
                print(f"    [INFO] Found {len(chapters)} chapters in embedded JSON tag.")
        except: pass

    # If no useful embedded JSON, hit the API using the required ASIN
    if not chapters:
        url = f"https://api.audnex.us/books/{asin}/chapters"
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                api_data = json.loads(response.read().decode())
                chapters = api_data.get("chapters")
                if chapters: print(f"    [INFO] Fetched {len(chapters)} chapters from API.")
        except Exception as e:
            print(f"    [!] API fetch failed: {e}")

    if not chapters:
        print("    [SKIP] ASIN present but no chapter data could be retrieved.")
        return

    # Chapter Injection
    should_inject = is_generic_chapters(all_tracks)
    base_name = os.path.splitext(filepath)[0]
    chapter_file = f"{base_name}.chapters.txt"

    with open(chapter_file, "w", encoding="utf-8", newline='\n') as f:
        for c in chapters:
            offset = c.get('startOffsetMs') if c.get('startOffsetMs') is not None else c.get('start_offset_ms')
            title = c.get('title', 'Unknown Chapter')
            if offset is not None:
                f.write(f"{format_timestamp(offset)} {title}\n")
    
    time.sleep(0.3)

    if should_inject:
        print("    [INFO] Injecting markers...")
        subprocess.run(["mp4chaps", "-r", filepath], capture_output=True)
        res = subprocess.run(["mp4chaps", "-i", filepath], capture_output=True, text=True)
        if res.returncode != 0: print(f"    [!] Injection error: {res.stderr.strip()}")

    # Organization
    def clean(text): return "".join(c for c in str(text) if c not in r'\/:*?"<>|').strip()
    c_author, c_series, c_year, c_album = clean(author), clean(series), clean(year), clean(album)

    new_dir = os.path.join(os.getcwd(), c_author, c_series, f"{c_year} - {c_album}")
    os.makedirs(new_dir, exist_ok=True)
    
    final_name = f"{c_author} - {c_series} - {c_year} - {c_album}"
    new_m4b = os.path.join(new_dir, f"{final_name}.m4b")
    new_txt = os.path.join(new_dir, f"{final_name}.chapters.txt")

    try:
        shutil.move(filepath, new_m4b)
        if os.path.exists(chapter_file): shutil.move(chapter_file, new_txt)
        print(f"    [DONE] Organized into: {c_author}/{c_series}")
    except Exception as e:
        print(f"    [!] Move error: {e}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    m4b_files = sorted(glob.glob("*.m4b"))
    print(f"SCRIPT START: Found {len(m4b_files)} M4B files.")
    for f in m4b_files:
        process_file(f)