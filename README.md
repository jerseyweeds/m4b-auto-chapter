# Audiobook Chapter Injector & Organizer

A specialized Python utility for macOS power users to automate the enrichment and organization of `.m4b` libraries. This script specializes in fixing "flat" audiobooks by injecting descriptive chapter titles and organizing them into a strict hierarchy optimized for **Plex**, **Prologue**, and **Audiobookshelf**.

## 🚀 Key Features

- **Smart Chapter Overwrite**: 
    - Automatically detects if existing chapters are generic (e.g., "Chapter 1", "1").
    - Detects "Single-Chapter Stubs" (one marker for the whole book) and replaces them with full data.
    - **Safe-Guard**: Skips injection if descriptive, multi-chapter titles already exist to preserve manual work.
- **Poisoned Metadata Filtering**: Ignores embedded JSON tags that contain incomplete or single-chapter data, forcing an API refresh for the full list.
- **Deep Metadata Extraction**: Leverages `MediaInfo` to extract hidden Audible ASINs (`CDEK`) and Base64 encoded metadata.
- **Automated Plex Organization**: Moves and renames files into a nested structure:
  `Author / Series / Year - Title / Author - Series - Year - Title.m4b`
- **Lossless Processing**: Clears old markers and injects new ones using `mp4chaps` without re-encoding the audio.

## 📋 Prerequisites

Install the necessary command-line dependencies via [Homebrew](https://brew.sh):

```bash
brew install mediainfo mp4v2
```

## 🛠️ Installation & Usage

1. **Download** the `auto_chapter.py` script to your audiobook staging folder.
2. **Permissions**: Ensure the script is executable:
   ```bash
   chmod +x auto_chapter.py
   ```
3. **Run**:
   ```bash
   python3 auto_chapter.py
   ```

## 📂 Final Library Structure

The script generates the following structure based on your specific requirements:

```text
/Isaac Asimov
    /Robots
        /2024 - The Complete Robot
            Isaac Asimov - Robots - 2024 - The Complete Robot.m4b
            Isaac Asimov - Robots - 2024 - The Complete Robot.chapters.txt
```

## ⚙️ How the "Smart Logic" Works

1. **Scan**: The script identifies all `.m4b` files in its current directory.
2. **Generic Check**: It inspects the first 3 chapters. If they are named "Chapter 1" or similar, or if there is only 1 chapter total, it flags the file for a "Full Update."
3. **Source Selection**:
   - **First**: It checks for an embedded JSON block with >1 chapter.
   - **Second**: It checks for a `CDEK` (ASIN) tag to pull from the Audnexus API.
   - **Third**: It performs a fuzzy search on Audnexus using the Title and Artist.
4. **Clean Slate**: If updating, it runs `mp4chaps -r` to remove existing stubs before injecting the new `.chapters.txt`.
5. **Relocate**: Sanitizes filenames (removing illegal characters like `:` or `/`) and moves the M4B and TXT pair to their new home.

## 🤝 Contributing

If you encounter a file that the script identifies as "Descriptive" but you believe should be overwritten, or if a specific metadata format is missed, please open an issue.

## ⚖️ License

Distributed under the MIT License.

