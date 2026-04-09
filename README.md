

# Audiobook Chapter Injector & Organizer (Strict Mode)

A specialized Python utility for macOS to automate the enrichment and organization of `.m4b` libraries. This script is designed for a **"Tag-First"** workflow, meaning it only processes files that already contain an Audible ASIN, ensuring a high-quality, verified library.

## 🚀 Key Features

- **Strict ASIN Gatekeeper**: Files without a `CDEK` (ASIN) tag are completely ignored. They will not be processed, injected, or moved.
- **Smart Chapter Overwrite**: 
    - Detects if existing chapters are generic (e.g., "Chapter 1", "1").
    - Detects "Single-Chapter Stubs" (one marker for the whole book) and replaces them with full descriptive data.
    - **Safe-Guard**: Skips injection if descriptive, multi-chapter titles already exist to preserve existing high-quality data.
- **Poisoned Metadata Filtering**: Detects and ignores embedded JSON tags that contain only a single chapter, forcing a refresh from the Audnexus API.
- **Automated Plex Organization**: Moves and renames files into a nested, clean structure:
  `Author / Series / Year - Title / Author - Series - Year - Title.m4b`
- **Lossless Processing**: Uses `mp4chaps` to clear old stubs and inject new markers without re-encoding the audio.

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

## 📂 Targeted Folder Structure

The script generates the following structure for files that pass the ASIN check:

```text
/Isaac Asimov
    /Robots
        /2024 - The Complete Robot
            Isaac Asimov - Robots - 2024 - The Complete Robot.m4b
            Isaac Asimov - Robots - 2024 - The Complete Robot.chapters.txt
```

## ⚙️ Logic Flow

1. **Scan**: Identifies all `.m4b` files in the current directory.
2. **ASIN Verification**: 
   - Uses `MediaInfo` to look for a `CDEK` tag.
   - **If missing**: Logs `[SKIP] No CDEK/ASIN tag found` and leaves the file untouched.
3. **Chapter Extraction**: 
   - Decodes embedded JSON if it contains multiple chapters.
   - Falls back to the Audnexus API using the verified ASIN.
4. **Injection**: If the existing chapters are generic or a single-file stub, it runs `mp4chaps -r` and then `mp4chaps -i`.
5. **Relocate**: Sanitizes metadata strings (removing characters like `:` or `/`) and moves both the M4B and the `.chapters.txt` to the final nested directory.

## ⚖️ License

Distributed under the MIT License.
