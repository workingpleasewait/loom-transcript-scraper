#!/usr/bin/env python3
"""
Script to integrate the LLM transcript preparation functionality with the existing loom-transcript-scraper.

This script can be used to add the ability to process transcripts for LLM use after they are downloaded,
while preserving folder integrity for future runs without overlap.
"""

import os
import re
import time
import string
import argparse
from pathlib import Path

# Import essential functions from process_transcripts_for_llm.py
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

def process_transcript(source_path, target_path):
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
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Process Loom transcripts for LLM usage.')
    parser.add_argument('--source-dir', type=str, default="/Users/mss/Desktop/BuildrWealth/Loom Transcripts",
                        help='Directory containing Loom transcript files (default: /Users/mss/Desktop/BuildrWealth/Loom Transcripts)')
    parser.add_argument('--target-dir', type=str, default="llm_ready_transcripts",
                        help='Directory to store LLM-ready transcripts (default: llm_ready_transcripts)')
    parser.add_argument('--force', action='store_true',
                        help='Force processing of transcripts even if they were previously processed')
    parser.add_argument('--suffix', type=str, default="_llm.txt",
                        help='Suffix to append to processed transcript files (default: _llm.txt)')
    args = parser.parse_args()

    # Ensure source directory exists
    if not os.path.exists(args.source_dir):
        print(f"Source directory {args.source_dir} does not exist!")
        return

    # Ensure target directory exists (create if it doesn't)
    if not os.path.exists(args.target_dir):
        os.makedirs(args.target_dir, exist_ok=True)
        print(f"Created target directory: {args.target_dir}")
    else:
        print(f"Using existing target directory: {args.target_dir}")

    # Get all transcript files from source directory
    transcript_files = [f for f in os.listdir(args.source_dir) if f.endswith('.txt')]
    
    if not transcript_files:
        print(f"No .txt files found in {args.source_dir}")
        return
    
    print(f"Found {len(transcript_files)} transcript files to process")
    
    # Process each file
    processed_count = 0
    skipped_count = 0
    
    start_time = time.time()
    
    for filename in transcript_files:
        source_file = os.path.join(args.source_dir, filename)
        
        # Extract the base name without extension
        name_without_ext = os.path.splitext(filename)[0]
        
        # Determine target filename
        if args.suffix.endswith('.txt'):
            # If suffix already includes .txt extension
            target_file = os.path.join(args.target_dir, f"{name_without_ext}{args.suffix}")
        else:
            # Otherwise append .txt
            target_file = os.path.join(args.target_dir, f"{name_without_ext}{args.suffix}")
        
        # Skip processing if the file already exists and --force not specified
        if os.path.exists(target_file) and not args.force:
            print(f"Skipping {filename} - already processed (use --force to process anyway)")
            skipped_count += 1
            continue
        
        # Process the file
        if process_transcript(source_file, target_file):
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
