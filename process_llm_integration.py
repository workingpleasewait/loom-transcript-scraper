#!/usr/bin/env python3
"""
process_llm_integration.py

This script updates the Loom transcript scraper to integrate LLM transcript processing.
It adds the necessary functionality to process transcripts for LLM use right after 
they are downloaded, while preserving folder structure and ensuring proper handling
for future runs without overlap.
"""

import os
import re
import time
import string
import shutil
import argparse
from pathlib import Path

# Function to modify process.py to include LLM transcript preparation
def update_process_script():
    """Updates the process.py script to include LLM transcript preparation functionality."""
    
    # Path to the original process.py script
    process_script_path = "process.py"
    
    # Backup the original script before making changes
    backup_path = "process.py.backup"
    if not os.path.exists(backup_path):
        shutil.copy2(process_script_path, backup_path)
        print(f"Backed up original process.py to {backup_path}")
    
    # Read the original script
    with open(process_script_path, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    # Check if the script has already been modified
    if "def clean_transcript(" in original_content:
        print("The process.py script has already been modified to include LLM transcript processing.")
        return False
    
    # The new imports to add
    new_imports = """import re
import string
"""
    
    # The LLM processing functions to add
    llm_functions = """
# LLM transcript processing functions
def clean_transcript(text):
    '''
    Process transcript text to make it LLM-friendly.
    
    Args:
        text (str): Raw transcript text
    
    Returns:
        str: Cleaned and formatted transcript text
    '''
    # Step 1: Preserve timestamps by standardizing their format to [HH:MM:SS]
    # Step 1: Preserve timestamps by standardizing their format to [HH:MM:SS]
    # This regex matches common timestamp formats and standardizes them
    text = re.sub(r'(\[?\(?\s*)(\d{1,2}:\d{2}(?:\d{2})?)\s*(?:\]|\))?', r'[\2]', text)
    # Step 2: Normalize line breaks and ensure speaker names are properly formatted
    # Step 2: Normalize line breaks and ensure speaker names are properly formatted
    # This helps maintain the conversation structure
    text = re.sub(r'\n{3,}', '\n\n', text)  # Replace excessive newlines with double newlines
    # Step 3: Fix common punctuation issues
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

def process_for_llm(transcript_filepath, llm_dir):
    '''Process a transcript file for LLM and save to the LLM directory.
    
    Args:
        transcript_filepath (str): Path to the transcript file
        llm_dir (str): Directory to save LLM-ready transcript
        
    Returns:
        bool: True if successful, False otherwise
    '''
    try:
        # Get the base filename
        base_name = os.path.basename(transcript_filepath)
        name_without_ext = os.path.splitext(base_name)[0]
        llm_filepath = os.path.join(llm_dir, f"{name_without_ext}_llm.txt")
        
        # Skip if already processed
        if os.path.exists(llm_filepath):
            print(f"LLM version already exists: {llm_filepath}")
            return False
        
        # Read the transcript
        with open(transcript_filepath, "r", encoding="utf-8") as f:
            transcript_text = f.read()
        
        # Clean and format for LLM
        processed_text = clean_transcript(transcript_text)
        
        # Save to LLM directory
        with open(llm_filepath, "w", encoding="utf-8") as f:
            f.write(processed_text)
        
        print(f"Created LLM-ready transcript: {llm_filepath}")
        return True
    except Exception as e:
        print(f"Error processing transcript for LLM: {str(e)}")
        return False
"""
    
    # Find the right spot to insert the new import statements
    import_insertion_point = original_content.find("import os")
    if import_insertion_point == -1:
        print("Could not find import statements in process.py")
        return False
    
    # Find the right spot to insert the LLM functions (before the main try block)
    function_insertion_point = original_content.find("try:")
    if function_insertion_point == -1:
        print("Could not find the main try block in process.py")
        return False
    
    # Add command-line argument for LLM processing
    arg_content = """parser.add_argument('--process-llm', action='store_true', 
                help='Process transcripts for LLM after downloading')
parser.add_argument('--llm-dir', type=str, default="llm_ready_transcripts",
                help='Directory to store LLM-ready transcripts (default: llm_ready_transcripts)')"""
    
    # Find the right spot to insert the new command-line arguments
    arg_insertion_point = original_content.find("args = parser.parse_args(")
    if arg_insertion_point == -1:
        print("Could not find the argument parsing section in process.py")
        return False
    
    # Find the line before args = parser.parse_args()
    last_arg_line = original_content.rfind("\n", 0, arg_insertion_point)
    if last_arg_line == -1:
        print("Could not find the end of argument definitions in process.py")
        return False
    
    # Add LLM directory creation
    dir_creation_code = """# Ensure LLM directory exists if processing for LLM
if args.process_llm:
    llm_dir = args.llm_dir
    if not os.path.exists(llm_dir):
        os.makedirs(llm_dir)
        print(f"Created directory for LLM-ready transcripts: {llm_dir}")
    else:
        print(f"Using existing directory for LLM-ready transcripts: {llm_dir}")
"""
    
    # Find the spot to insert directory creation code (after download_dir creation)
    dir_insertion_point = original_content.find("if not os.path.exists(download_dir):")
    dir_code_end = original_content.find("else:", dir_insertion_point)
    dir_code_end = original_content.find("\n", dir_code_end) + 1
    
    # Add LLM processing call after saving transcript to file
    llm_processing_code = """                    # Process for LLM if requested
                if args.process_llm:
                    process_for_llm(transcript_filepath, args.llm_dir)
"""
    
    # Find the spot to insert LLM processing code (after saving transcript)
    processing_insertion_point = original_content.find('print(f"Transcript saved to: {transcript_filepath}")')
    if processing_insertion_point == -1:
        print("Could not find the transcript saving section in process.py")
        return False
    processing_insertion_point = original_content.find("\n", processing_insertion_point) + 1
    
    # Construct the modified content
    modified_content = (
        original_content[:import_insertion_point] + 
        new_imports + 
        original_content[import_insertion_point:last_arg_line + 1] + 
        arg_content + 
        original_content[last_arg_line + 1:dir_code_end] + 
        dir_creation_code + 
        original_content[dir_code_end:function_insertion_point] + 
        llm_functions + 
        original_content[function_insertion_point:processing_insertion_point] + 
        llm_processing_code + 
        original_content[processing_insertion_point:]
    )
    
    # Write the modified content back to the file
    with open(process_script_path, 'w', encoding='utf-8') as f:
        f.write(modified_content)
    
    print("Successfully updated process.py with LLM transcript processing functionality")
    return True

def main():
    parser = argparse.ArgumentParser(description='Integrate LLM transcript processing into the Loom scraper.')
    parser.add_argument('--restore', action='store_true',
                        help='Restore the original process.py from backup')
    args = parser.parse_args()
    
    if args.restore:
        backup_path = "process.py.backup"
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, "process.py")
            print("Restored original process.py from backup")
        else:
            print("No backup file found (process.py.backup)")
    else:
        update_process_script()
        print("\nTo use the LLM processing functionality, run process.py with the --process-llm flag:")
        print("python process.py --process-llm")
        print("\nYou can specify a custom directory for LLM-ready transcripts:")
        print("python process.py --process-llm --llm-dir custom_llm_dir")
        print("\nTo restore the original process.py script:")
        print("python process_llm_integration.py --restore")

if __name__ == "__main__":
    main()
