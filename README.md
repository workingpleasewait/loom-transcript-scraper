# Loom Transcript Scraper

A tool for automatically extracting transcripts from Loom videos using Selenium web automation.

## Overview

This project provides a Python-based solution for scraping transcripts from Loom video URLs. It uses Selenium WebDriver to automate browser interactions, navigate to Loom video pages, and extract transcript content.

## Features

- Automated browser navigation to Loom video pages
- Transcript extraction from Loom's internal data structure
- Robust error handling with detailed debugging
- Support for processing multiple videos in batch
- LLM transcript processing capabilities for AI model ingestion

## Prerequisites

- Python 3.x
- Chrome or Firefox web browser
- Selenium WebDriver
- Required Python packages (see Installation)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/workingpleasewait/loom-transcript-scraper.git
   cd loom-transcript-scraper
   ```

2. Install required packages:
   ```
   pip3 install selenium webdriver_manager
   ```

3. Ensure your browser driver is properly configured.

## Usage

1. Add Loom video URLs to the `loom-videos.txt` file, one URL per line.

2. Run the processor script:
   ```
   python3 process.py
   ```

3. Extracted transcripts will be saved in the `data/` directory.

## Project Structure

- `process.py` - Main script for processing Loom videos and extracting transcripts
- `debug.py` - Helper script with debug functionality
- `loom-videos.txt` - Input file containing Loom video URLs to process
- `data/` - Directory where extracted transcripts are stored
- `debug_screenshots/` - Directory for browser screenshots (for debugging)
- `debug_output/` - Directory for HTML page sources and button information (for debugging)
- `integrated_solution.py` - Integration script for LLM processing
- `process_llm_integration.py` - Handles LLM transcript processing integration
- `process_transcripts_for_llm.py` - Processes transcripts for LLM ingestion
- `README_LLM_INTEGRATION.md` - Detailed guide for LLM integration
- `IMPLEMENTATION_GUIDE.md` - Implementation guide for LLM processing

## Debug Directories

This project includes two special directories for debugging purposes:

### debug_screenshots/

This directory stores browser screenshots taken at various stages of the scraping process. These screenshots are valuable for troubleshooting when the script encounters issues with page rendering, element visibility, or automation steps.

The screenshots are named according to the processing stage and timestamp, allowing developers to trace the execution path visually.

### debug_output/

This directory contains:
- HTML page sources for problematic pages
- JSON files with detailed information about buttons and interactive elements
- Shadow DOM information and other page structural details

These files provide context and data needed to debug complex web scraping issues, particularly when the target elements are located within shadow DOM or are dynamically loaded.

## LLM Transcript Processing

This project includes functionality to process Loom video transcripts for ingestion into Large Language Models (LLMs). The processing:

- Formats transcripts in a standardized way for optimal LLM consumption
- Cleans and structures text for better AI processing
- Supports both integrated and standalone usage approaches

For detailed information about using the LLM transcript processing features, refer to:
- `README_LLM_INTEGRATION.md` - Contains integration guidelines
- `IMPLEMENTATION_GUIDE.md` - Provides detailed implementation steps

## LLM Transcript Directory Organization

Transcripts prepared for LLM ingestion are organized as follows:

- Raw transcripts are stored in the configured download directory
- LLM-ready transcripts are stored in the `llm_ready_transcripts/` directory
- Each LLM-ready file is named with the video title and ID, with an '_llm' suffix
- The directory structure preserves the relationship between original videos and their processed transcripts

## Troubleshooting

If the script fails to extract a transcript:

1. Check the `debug_screenshots` directory for visual references of the browser state
2. Examine the `debug_output` directory for page structure information
3. Ensure the Loom video has a transcript (not all videos do)
4. Verify your browser driver is up to date

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).
