

---

# Audiobook Chapter Injector & Organizer

A robust Python utility for macOS designed to automate the lifecycle of `.m4b` audiobooks. This script extracts metadata (including hidden Audible ASINs), fetches or decodes chapter titles, injects them losslessly into the file, and organizes your library into a Plex-ready directory structure.

## 🚀 Features

- **Deep Metadata Extraction**: Uses `MediaInfo` to find hidden `CDEK` (ASIN) tags and Base64 encoded JSON blocks.
- **Smart Chapter Fetching**: If chapters aren't embedded, the script automatically queries the **Audnexus API** to find high-quality chapter titles.
- **Lossless Injection**: Uses `mp4chaps` to bake markers into the `.m4b` container without re-encoding the audio.
- **Library Organization**: Automatically moves and renames files into a structured hierarchy:
  `Author / Series / Year - Title / Author - Series - Year - Title.m4b`
- **Error Handling**: Gracefully skips files with missing metadata or network issues.

## 📋 Prerequisites

This script requires two industry-standard command-line tools available via [Homebrew](https://brew.sh).

```bash
brew install mediainfo mp4v2
```

*Note: No `pip install` is required as the script utilizes the Python Standard Library.*

## 🛠️ Installation & Usage

1. **Clone the repository** or download the `auto_chapter.py` script.
2. **Place the script** in the folder containing your `.m4b` files.
3. **Run the script**:
   ```bash
   python3 auto_chapter.py
   ```

## 📂 Output Structure

The script transforms your flat files into an organized library compatible with **Plex**, **Audiobookshelf**, and mobile clients like **Prologue**.

**Before:**
```text
Cryptonomicon.m4b
Foundation.m4b
```

**After:**
```text
/Neal Stephenson
    /Non-Series
        /2020 - Cryptonomicon
            Neal Stephenson - Non-Series - 2020 - Cryptonomicon.m4b
            Neal Stephenson - Non-Series - 2020 - Cryptonomicon.chapters.txt

/Isaac Asimov
    /Foundation
        /1951 - Foundation
            Isaac Asimov - Foundation - 1951 - Foundation.m4b
            Isaac Asimov - Foundation - 1951 - Foundation.chapters.txt
```

## ⚙️ How it Works

1. **Scan**: Identifies all `.m4b` files in the current directory.
2. **Identify**: Uses `mediainfo` to look for an Audible Product ID (ASIN).
3. **Retrieve**: 
   - Attempts to decode a Base64 `JSON` tag if present.
   - Falls back to the Audnexus API if only an ASIN is found.
4. **Write**: Generates a `.chapters.txt` file and uses `mp4chaps` to import it into the M4B.
5. **Move**: Sanitizes metadata strings and moves the files to the final destination.

## 🤝 Contributing

Contributions are welcome! If you find a tag format that isn't being recognized, please open an issue with the `ffprobe` or `mediainfo` output.

## ⚖️ License

Distributed under the MIT License. See `LICENSE` for more information.

---
