# Loom Transcript Scraper with LLM Processing

This project extends the existing loom-transcript-scraper to add automatic preparation of transcripts for use with Large Language Models (LLMs).

## Overview

The integration adds the ability to:

1. Process downloaded Loom transcripts to make them more suitable for use with LLMs
2. Preserve folder integrity and maintain proper organization for future runs
3. Run the processing either as part of the scraping process or as a separate step

## Features Added

- Timestamps standardization to a consistent format (e.g., `[0:00]`)
- Normalization of whitespace and line breaks
- Proper punctuation formatting
- Removal of empty or extraneous lines
- Filtering of non-printable characters
- Preservation of paragraph structure and conversation flow

## How to Use

### Option 1: Integrated Processing During Scraping

To automatically process transcripts for LLM use as they're downloaded:

```bash
python process.py --process-llm
```

This will:
1. Download transcripts as usual
2. Process each transcript to make it LLM-friendly
3. Save processed transcripts to the "llm_ready_transcripts" directory with "_llm.txt" appended to filenames

You can specify a custom directory for the processed transcripts:

```bash
python process.py --process-llm --llm-dir custom_directory
```

### Option 2: Standalone Processing of Existing Transcripts

If you already have transcripts downloaded and want to process them separately:

```bash
python integrated_solution.py
```

Additional options:
- `--source-dir`: Specify the directory containing transcripts (default: "/Users/mss/Desktop/BuildrWealth/Loom Transcripts")
- `--target-dir`: Specify where to save processed transcripts (default: "llm_ready_transcripts")
- `--force`: Process transcripts even if they were previously processed
- `--suffix`: Change the suffix added to processed files (default: "_llm.txt")

Example:
```bash
python integrated_solution.py --source-dir "my_transcripts" --target-dir "llm_ready" --force
```

## Implementation Details

The integration consists of two main components:

1. `integrated_solution.py`: A standalone script that processes existing transcript files
2. `process_llm_integration.py`: A utility that modifies the main scraper script to include LLM processing

### How to Enable the Integration

Run the following command to update the main scraper script:

```bash
python process_llm_integration.py
```

This will:
- Create a backup of the original `process.py` file
- Add the necessary code to process transcripts for LLM use
- Add command-line arguments for LLM processing

To restore the original script:

```bash
python process_llm_integration.py --restore
```

## Processing Logic

The transcript processing:

1. Preserves timestamps by standardizing their format
2. Normalizes line breaks and whitespace
3. Fixes punctuation issues (spacing, duplicates)
4. Removes empty lines while maintaining paragraph structure
5. Filters out non-printable characters

## File Organization

- Original transcripts: Stored in the regular download directory
- LLM-ready transcripts: Stored in a separate directory with "_llm.txt" suffix
- This organization ensures clear separation and prevents any overlap or confusion

## Idempotence

The processing is idempotent - running it multiple times will not duplicate work or create additional files. It automatically skips files that have already been processed unless the `--force` flag is specified.
