#!/usr/bin/env python3
"""
process_transcripts_for_llm.py

This script processes Loom transcript files to make them more suitable for use with LLMs.
It reads all .txt files from a specified source directory, cleans and formats them,
and saves the processed files to a target directory with "_llm.txt" appended to the filename.

The script is designed to be idempotent and will skip files that have already been processed.
"""

import os
import re
import glob
import time
import string
from pathlib import Path

# Define source and target directories
SOURCE_DIR = "/Users/mss/Desktop/BuildrWealth/Loom Transcripts"
TARGET_DIR = "/Users/mss/loom-transcript-scraper/llm_ready_transcripts"

def clean_transcript(text):
    """
    Process transcript text to make it LLM-friendly.
    
    Args:
        text (str): Raw transcript text
    
    Returns:
        str: Cleaned and formatted transcript text
    """
    # Step 1: Preserve timestamps by standardizing their format to [HH:MM:SS]
    # This regex matches common timestamp formats and standardizes them
    text = re.sub(r'(\[?\(?\s*)(\d{1,2}:\d{2}(?::\d{2})?)\s*(?:\]|\))?', r'[\2]', text)
    
    # Step 2: Normalize line breaks and ensure speaker names are properly formatted
    # This helps maintain the conversation structure
    text = re.sub(r'\n{3,}', '\n\n', text)  # Replace excessive newlines with double newlines
    
    # Step 3: Fix common punctuation issues
    # Remove duplicate punctuation and ensure proper spacing
    text = re.sub(r'([.!?])\s*([.!?])+', r'\1', text)  # Remove duplicate punctuation
    text = re.sub(r'\s+([.,;:!?])', r'\1', text)  # Remove space before punctuation
    text = re.sub(r'([.,;:!?])([^\s\d])', r'\1 \2', text)  # Add space after punctuation if missing
    
    # Step 4: Normalize whitespace
    # Remove trailing/leading whitespace from each line and collapse multiple spaces
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)
    text = re.sub(r' +', ' ', text)  # Replace multiple spaces with a single space
    
    # Step 5: Remove empty lines while preserving paragraph structure
    lines = text.split('\n')
    non_empty_lines = []
    for i, line in enumerate(lines):
        # Keep the line if it's not empty or if it's a deliberate paragraph break
        if line.strip() or (i > 0 and i < len(lines) - 1 and lines[i-1].strip() and lines[i+1].strip()):
            non_empty_lines.append(line)
    
    # Step 6: Final cleanup - remove any remaining problematic characters
    # (but carefully preserve important special characters)
    text = '\n'.join(non_empty_lines)
    
    # Filter out any non-printable characters except for common line breaks
    printable_chars = set(string.printable)
    text = ''.join(c for c in text if c in printable_chars)
    
    return text

def process_file(source_path, target_path):
    """
    Process a single transcript file.
    
    Args:
        source_path (str): Path to the source transcript file
        target_path (str): Path to save the processed file
    
    Returns:
        bool: True if file was processed, False if skipped
    """
    # Check if target file already exists (idempotence)
    if os.path.exists(target_path):
        print(f"Skipping {os.path.basename(source_path)} - already processed")
        return False
    
    try:
        # Read source file
        with open(source_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Clean and format the transcript
        processed_content = clean_transcript(content)
        
        # Save processed content to target file
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(processed_content)
        
        print(f"Processed: {os.path.basename(source_path)} -> {os.path.basename(target_path)}")
        return True
    except Exception as e:
        print(f"Error processing {source_path}: {str(e)}")
        return False

def main():
    """
    Main function to process all transcript files.
    """
    # Ensure target directory exists
    os.makedirs(TARGET_DIR, exist_ok=True)
    
    # Get all .txt files from source directory
    transcript_files = glob.glob(os.path.join(SOURCE_DIR, "*.txt"))
    
    if not transcript_files:
        print(f"No .txt files found in {SOURCE_DIR}")
        return
    
    print(f"Found {len(transcript_files)} transcript files to process")
    
    # Process each file
    processed_count = 0
    skipped_count = 0
    
    start_time = time.time()
    
    for source_file in transcript_files:
        # Generate target filename by appending "_llm.txt" to the original name
        base_name = os.path.basename(source_file)
        name_without_ext = os.path.splitext(base_name)[0]
        target_file = os.path.join(TARGET_DIR, f"{name_without_ext}_llm.txt")
        
        # Process the file
        if process_file(source_file, target_file):
            processed_count += 1
        else:
            skipped_count += 1
    
    # Report summary
    elapsed_time = time.time() - start_time
    print(f"\nProcessing complete!")
    print(f"Total files: {len(transcript_files)}")
    print(f"Processed: {processed_count}")
    print(f"Skipped: {skipped_count}")
    print(f"Time taken: {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    main()

