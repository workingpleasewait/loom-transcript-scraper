# Step-by-Step Guide to Implementing LLM Transcript Processing

This guide will walk you through integrating LLM transcript processing into your existing loom-transcript-scraper in a way that maintains folder integrity and ensures smooth operation for future runs.

## Step 1: Backup Your Files

Before making any changes, create a backup of your existing setup:

```bash
# Backup your main script
cp process.py process.py.original
```

## Step 2: Integrate the LLM Processing Functionality

You have two options for integration:

### Option A: Automatic Integration (Recommended)

Run the integration script to automatically update your `process.py` file:

```bash
python process_llm_integration.py
```

This will:
- Add LLM processing functions to your main script
- Add command-line arguments for controlling LLM processing
- Create a backup of your original script (as `process.py.backup`)

### Option B: Manual Integration

If you prefer to manually integrate the changes or have a heavily customized `process.py`:

1. Copy the `clean_transcript()` and `process_for_llm()` functions from `integrated_solution.py`
2. Add these functions to your `process.py` file
3. Add the command-line arguments for LLM processing
4. Add the code to create the LLM directory
5. Add the call to process transcripts after saving them

## Step 3: Using the Integrated Functionality

### Method 1: Process Transcripts While Scraping

To download and process transcripts in one step:

```bash
python process.py --process-llm
```

This will:
1. Download transcripts from Loom as usual
2. Process each transcript for LLM use
3. Save processed transcripts to the `llm_ready_transcripts` directory

You can specify a custom directory for LLM-ready transcripts:

```bash
python process.py --process-llm --llm-dir custom_directory
```

### Method 2: Process Existing Transcripts

If you already have transcripts downloaded and want to process them separately:

```bash
python integrated_solution.py
```

For customization:

```bash
python integrated_solution.py --source-dir "my_transcripts" --target-dir "llm_ready" --force
```

## Step 4: Verifying the Integration

After running the processing, check that:

1. The original transcripts remain intact in their original location
2. Processed transcripts are stored in the target directory with the "_llm.txt" suffix
3. The processing has correctly preserved timestamps and formatted the text

Example verification:

```bash
# List the processed transcripts
ls -la llm_ready_transcripts/

# Compare an original transcript with its processed version
diff -y --suppress-common-lines "original_transcript.txt" "llm_ready_transcripts/original_transcript_llm.txt"
```

## Step 5: Reverting Changes (If Needed)

If you need to revert to the original script:

```bash
python process_llm_integration.py --restore
```

Or manually restore from your backup:

```bash
cp process.py.original process.py
```

## Common Use Cases

### Scenario 1: Regular Workflow with LLM Processing

```bash
# Add Loom video URLs to loom-videos.txt
# Then run:
python process.py --process-llm
```

### Scenario 2: Batch Processing Existing Transcripts

```bash
python integrated_solution.py --force
```

### Scenario 3: Processing Transcripts to a Different Location

```bash
python process.py --process-llm --llm-dir "/path/to/llm_transcripts"
```

## Troubleshooting

**Issue**: No transcripts are being processed for LLM
**Solution**: Check if the source directory contains transcript files and that you're using the correct path

**Issue**: Error when running the integrated script
**Solution**: Ensure all required packages are installed (`string`, `re`, etc.)

**Issue**: Processed transcripts missing timestamps
**Solution**: Check the regex pattern in `clean_transcript()` function and adjust if needed for your specific format

**Issue**: Original script functionality broke after integration
**Solution**: Restore from backup and try the manual integration approach
