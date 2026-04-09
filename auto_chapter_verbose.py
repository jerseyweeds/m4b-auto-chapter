import json
import subprocess
import urllib.request
import os
import base64
import glob
import shutil

def format_timestamp(ms):
    """Converts milliseconds to HH:MM:SS.mmm."""
    hours, ms = divmod(ms, 3600000)
    minutes, ms = divmod(ms, 60000)
    seconds = ms / 1000.0
    return f"{int(hours):02}:{int(minutes):02}:{seconds:06.3f}"

def get_mediainfo_data(filepath):
    """Uses MediaInfo CLI to get a full JSON metadata dump."""
    cmd = ["mediainfo", "--Output=JSON", filepath]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        tracks = data.get("media", {}).get("track", [])
        for track in tracks:
            if track.get("@type") == "General":
                return track
    except Exception:
        return {}

def process_file(filepath):
    print(f"\n>>> Processing: {os.path.basename(filepath)}")
    general_track = get_mediainfo_data(filepath)
    extra_tags = general_track.get("extra", {})
    
    # 1. Extract metadata for organization
    author = general_track.get("Performer") or general_track.get("Artist") or "Unknown Author"
    album = general_track.get("Album") or general_track.get("Title") or "Unknown Album"
    year = general_track.get("Recorded_Date") or general_track.get("Released_Date") or "0000"
    series = extra_tags.get("series") or "Non-Series"
    
    # Clean Year to first 4 digits
    year = str(year)[:4]
    
    asin = general_track.get("CDEK") or extra_tags.get("CDEK")
    chapters = None

    # 2. Extract Chapters (Embedded JSON or API Fallback)
    json_val = extra_tags.get("JSON") or general_track.get("JSON")
    if json_val:
        try:
            try:
                decoded = base64.b64decode(json_val).decode('utf-8')
                json_data = json.loads(decoded)
            except:
                json_data = json.loads(json_val)
            chapters = json_data.get("chapters")
        except: pass

    if not chapters and asin:
        url = f"https://api.audnex.us/books/{asin}/chapters"
        try:
            with urllib.request.urlopen(url) as response:
                api_data = json.loads(response.read().decode())
                chapters = api_data.get("chapters")
        except: pass

    if not chapters:
        print("    [SKIP] No Chapter data found.")
        return

    # 3. Create temporary .chapters.txt next to original .m4b
    base_name = os.path.splitext(filepath)[0]
    temp_chapter_file = f"{base_name}.chapters.txt"
    with open(temp_chapter_file, "w") as f:
        for c in chapters:
            offset = c.get('startOffsetMs') if c.get('startOffsetMs') is not None else c.get('start_offset_ms')
            title = c.get('title', 'Unknown Chapter')
            if offset is not None:
                f.write(f"{format_timestamp(offset)} {title}\n")

    # 4. Inject chapters into original file
    subprocess.run(["mp4chaps", "-i", filepath], capture_output=True)
    print("    [SUCCESS] Chapters injected.")

    # 5. Define Folder and Filename naming
    def clean(text): 
        # Removes characters illegal in macOS/Windows paths
        return "".join(c for c in str(text) if c not in r'\/:*?"<>|').strip()

    # Cleaned metadata components
    c_author = clean(author)
    c_series = clean(series)
    c_year = clean(year)
    c_album = clean(album)

    # Subfolder Path: Author / Series / Year - Title
    new_dir = os.path.join(os.getcwd(), c_author, c_series, f"{c_year} - {c_album}")
    os.makedirs(new_dir, exist_ok=True)
    
    # Filename: Author - Series - Year - Title.m4b
    new_base_filename = f"{c_author} - {c_series} - {c_year} - {c_album}"
    
    new_m4b_path = os.path.join(new_dir, f"{new_base_filename}.m4b")
    new_txt_path = os.path.join(new_dir, f"{new_base_filename}.chapters.txt")

    # 6. Move and rename both files
    try:
        shutil.move(filepath, new_m4b_path)
        shutil.move(temp_chapter_file, new_txt_path)
        print(f"    [MOVED] {new_m4b_path}")
    except Exception as e:
        print(f"    [ERROR] Move failed: {e}")

if __name__ == "__main__":
    m4b_files = sorted(glob.glob("*.m4b"))
    if not m4b_files:
        print("No .m4b files found in current directory.")
    else:
        for f in m4b_files:
            process_file(f)