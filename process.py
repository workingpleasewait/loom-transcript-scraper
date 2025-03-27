from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import tempfile
import json
import argparse
# Parse command-line arguments
parser = argparse.ArgumentParser(description='Extract transcripts from Loom videos.')
parser.add_argument('--input-file', type=str, default='loom-videos.txt',
                    help='Path to the file containing Loom video URLs (default: loom-videos.txt)')
parser.add_argument('--force', action='store_true', 
                    help='Force processing of videos even if they were previously processed')
parser.add_argument('--preserve', action='store_true', 
                    help='Preserve the input file after processing (do not clear it)')
args = parser.parse_args()

# File paths
input_file = args.input_file
processed_file = "loom-videos-processed.txt"
download_dir = "/Users/mss/Desktop/BuildrWealth/Loom Transcripts"

# Initialize set of processed videos
processed_videos = set()

# Check if processed file exists and load already processed videos
if os.path.exists(processed_file):
    with open(processed_file, "r") as f:
        processed_videos = set(line.strip() for line in f if line.strip())
    print(f"Loaded {len(processed_videos)} previously processed videos from {processed_file}")

# Ensure download directory exists
if not os.path.exists(download_dir):
    os.makedirs(download_dir)
    print(f"Created download directory: {download_dir}")
else:
    print(f"Using existing download directory: {download_dir}")
# Create a temporary directory for the Chrome user data
temp_dir = tempfile.mkdtemp()
print(f"Using temporary directory for Chrome profile: {temp_dir}")

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument(f"user-data-dir={temp_dir}")
chrome_options.add_argument("--no-first-run")
chrome_options.add_argument("--no-default-browser-check")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)
chrome_options.binary_location = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"

# Set download directory preference
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
})
# Set up ChromeDriver service
service = Service(ChromeDriverManager().install())

# Initialize the WebDriver
driver = None

try:
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(30)

    # Navigate to Loom login page
    print("Navigating to Loom login page...")
    driver.get("https://www.loom.com/login")
    time.sleep(5)

    print("Please log in to your Loom account manually in the opened browser.")
    input("Press Enter when you have successfully logged in...")

    # Now proceed with the Loom video processing
    video_ids = [line.strip() for line in open(input_file, "r") if line.strip()]

    for video_id in video_ids:
        try:
            # Check if video has already been processed
            if not args.force and video_id in processed_videos:
                print(f"Skipping {video_id} - already processed (use --force to process anyway)")
                continue
                
            # Check if a transcript file for this video already exists
            clean_video_id = video_id.replace("https://www.loom.com/share/", "").replace("/", "_")
            existing_files = [f for f in os.listdir(download_dir) if clean_video_id in f and f.endswith(".txt")]
            
            if not args.force and existing_files:
                print(f"Skipping {video_id} - transcript file already exists: {existing_files[0]} (use --force to process anyway)")
                # Add to processed list if not already there
                if video_id not in processed_videos:
                    with open(processed_file, "a") as f:
                        f.write(f"{video_id}\n")
                    processed_videos.add(video_id)
                continue
            elif args.force and existing_files:
                print(f"Force processing {video_id} even though transcript file already exists: {existing_files[0]}")
            
            # Check if the video_id already contains the full URL
            if "https://www.loom.com/share/" in video_id:
                url = video_id
            else:
                url = f"https://www.loom.com/share/{video_id}"
            print(f"\nOpening URL: {url}")
            driver.get(url)

            print("Waiting for page to load...")
            time.sleep(10)  # Increased wait time to 10 seconds

            print("Current page title:", driver.title)

            # Taking screenshot for debugging
            screenshot_dir = "debug_screenshots"
            os.makedirs(screenshot_dir, exist_ok=True)
            screenshot_path = os.path.join(screenshot_dir, f"loom_{video_id.replace('/', '_')}.png")
            driver.save_screenshot(screenshot_path)
            print(f"Screenshot saved to {screenshot_path}")

            # Enhanced Debug Function
            def comprehensive_debug():
                debug_dir = "debug_output"
                os.makedirs(debug_dir, exist_ok=True)
                
                # 1. Save page source to file
                page_source_path = os.path.join(debug_dir, f"page_source_{video_id.replace('/', '_')}.html")
                with open(page_source_path, "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                print(f"Page source saved to {page_source_path}")
                
                # 2. Check for iframes
                iframes = driver.find_elements(By.TAG_NAME, "iframe")
                print(f"Found {len(iframes)} iframes on the page")
                for i, iframe in enumerate(iframes):
                    iframe_id = iframe.get_attribute("id") or "no-id"
                    iframe_src = iframe.get_attribute("src") or "no-src"
                    print(f"  Iframe {i+1}: ID={iframe_id}, Src={iframe_src}")
                
                # 3. List all buttons
                buttons = driver.find_elements(By.TAG_NAME, "button")
                print(f"Found {len(buttons)} buttons on the page")
                buttons_info = []
                for i, button in enumerate(buttons):
                    try:
                        button_text = button.text
                        button_class = button.get_attribute("class") or "no-class"
                        button_id = button.get_attribute("id") or "no-id"
                        is_displayed = button.is_displayed()
                        is_enabled = button.is_enabled()
                        buttons_info.append({
                            "index": i+1,
                            "text": button_text,
                            "class": button_class,
                            "id": button_id,
                            "is_displayed": is_displayed,
                            "is_enabled": is_enabled
                        })
                        print(f"  Button {i+1}: '{button_text[:30]}{'...' if len(button_text) > 30 else ''}', " +
                              f"Class={button_class}, ID={button_id}, " +
                              f"Displayed={is_displayed}, Enabled={is_enabled}")
                    except Exception as e:
                        print(f"  Button {i+1}: Error getting details: {str(e)}")
                
                # Save buttons info to file
                buttons_info_path = os.path.join(debug_dir, f"buttons_info_{video_id.replace('/', '_')}.json")
                with open(buttons_info_path, "w", encoding="utf-8") as f:
                    json.dump(buttons_info, f, indent=2)
                print(f"Buttons info saved to {buttons_info_path}")
                
                # 4. Check for shadow DOM elements
                print("Checking for shadow DOM elements...")
                shadow_hosts = driver.execute_script("""
                    return Array.from(document.querySelectorAll('*')).filter(
                        el => el.shadowRoot !== null
                    ).map(el => {
                        return {
                            tag: el.tagName.toLowerCase(),
                            id: el.id || 'no-id',
                            class: el.className || 'no-class'
                        };
                    });
                """)
                
                print(f"Found {len(shadow_hosts)} shadow DOM hosts on the page")
                for i, host in enumerate(shadow_hosts):
                    print(f"  Shadow Host {i+1}: <{host['tag']}> ID={host['id']}, Class={host['class']}")
                
                # Save shadow host info to file
                shadow_info_path = os.path.join(debug_dir, f"shadow_dom_info_{video_id.replace('/', '_')}.json")
                with open(shadow_info_path, "w", encoding="utf-8") as f:
                    json.dump(shadow_hosts, f, indent=2)
                print(f"Shadow DOM info saved to {shadow_info_path}")

            # Run the comprehensive debug
            comprehensive_debug()

            # Check for and switch to iframes
            print("\nChecking for iframes that might contain the transcript...")
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            main_window = driver.current_window_handle
            transcript_found_in_iframe = False
            
            for i, iframe in enumerate(iframes):
                try:
                    iframe_id = iframe.get_attribute("id") or "no-id"
                    print(f"Switching to iframe {i+1} (ID: {iframe_id})...")
                    driver.switch_to.frame(iframe)
                    
                    # Take screenshot of iframe content
                    iframe_screenshot_path = os.path.join(screenshot_dir, f"iframe_{i+1}_{video_id.replace('/', '_')}.png")
                    driver.save_screenshot(iframe_screenshot_path)
                    print(f"Iframe screenshot saved to {iframe_screenshot_path}")
                    
                    # Check if transcript elements exist in this iframe
                    transcript_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Transcript')]")
                    download_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Download')]")
                    
                    if transcript_elements or download_elements:
                        print(f"Found potential transcript elements in iframe {i+1}!")
                        transcript_found_in_iframe = True
                        break
                    else:
                        print(f"No transcript elements found in iframe {i+1}")
                        driver.switch_to.default_content()
                except Exception as e:
                    print(f"Error switching to iframe {i+1}: {str(e)}")
                    driver.switch_to.default_content()
            
            if not transcript_found_in_iframe:
                driver.switch_to.default_content()
                print("Switched back to main content (no transcript found in iframes)")
            
            # Debug: Find and print information about elements containing keywords
            print("\n--- DEBUG: Searching for relevant elements ---")
            for keyword in ["Transcript", "Activity", "Download"]:
                elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{keyword}')]")
                print(f"\nFound {len(elements)} elements containing '{keyword}':")
                for i, element in enumerate(elements):
                    tag_name = element.tag_name
                    try:
                        element_text = element.text
                        element_class = element.get_attribute("class") or "no-class"
                        element_id = element.get_attribute("id") or "no-id"
                        is_displayed = element.is_displayed()
                        is_enabled = element.is_enabled()
                        
                        # Get the XPath of the element
                        xpath = driver.execute_script("""
                            function getPathTo(element) {
                                if (element.id !== '')
                                    return '//*[@id="' + element.id + '"]';
                                if (element === document.body)
                                    return '/html/body';
                                
                                var ix = 0;
                                var siblings = element.parentNode.childNodes;
                                for (var i = 0; i < siblings.length; i++) {
                                    var sibling = siblings[i];
                                    if (sibling === element)
                                        return getPathTo(element.parentNode) + '/' + element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
                                    if (sibling.nodeType === 1 && sibling.tagName === element.tagName)
                                        ix++;
                                }
                            }
                            return getPathTo(arguments[0]);
                        """, element)
                        
                        print(f"  {i+1}. <{tag_name}> - Text: '{element_text[:30]}{'...' if len(element_text) > 30 else ''}' - Class: {element_class}")
                        print(f"     ID: {element_id}, Displayed: {is_displayed}, Enabled: {is_enabled}")
                        print(f"     XPath: {xpath}")
                        
                        # Print parent element info to understand context
                        try:
                            parent = driver.execute_script("return arguments[0].parentNode;", element)
                            parent_tag = driver.execute_script("return arguments[0].tagName;", parent).lower()
                            parent_class = driver.execute_script("return arguments[0].className;", parent) or "no-class"
                            print(f"     Parent: <{parent_tag}> - Class: {parent_class}")
                        except:
                            print("     Could not get parent info")
                    except Exception as e:
                        print(f"  {i+1}. <{tag_name}> - Error getting details: {str(e)}")
            print("--- END DEBUG ---\n")

            print("Looking for 'Transcript' section...")
            # Wait for the page to fully load to ensure the Transcript section is visible
            time.sleep(3)
            
            # First, try to find and click on the Transcript tab if it's not already active
            try:
                # Try to find using specific class name or text content
                transcript_tab = None
                try:
                    # First attempt: Using the specific class name
                    transcript_tab = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.css-1qz66q8"))
                    )
                    print("Found Transcript tab by class name. Clicking...")
                except:
                    # Second attempt: Using text content
                    try:
                        transcript_tab = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[text()='Transcript']"))
                        )
                        print("Found Transcript tab by exact text. Clicking...")
                    except:
                        # Third attempt: Using contains text
                        transcript_tab = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Transcript')]"))
                        )
                        print("Found Transcript tab by partial text. Clicking...")
                
                # Click the transcript tab
                transcript_tab.click()
                print("Clicked on Transcript tab. Waiting for content to load...")
                
                # Wait longer after clicking the tab
                time.sleep(5)
                
                # Take a screenshot after clicking the Transcript tab
                transcript_screenshot_path = os.path.join(screenshot_dir, f"transcript_tab_{video_id.replace('/', '_')}.png")
                driver.save_screenshot(transcript_screenshot_path)
                print(f"Screenshot after clicking Transcript tab saved to {transcript_screenshot_path}")
                
                # Debug: Print elements that appear after switching to Transcript tab
                print("\n--- DEBUG: Elements after switching to Transcript tab ---")
                for keyword in ["Download", "Toggle", "Transcript", "Copy", "Action"]:
                    elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{keyword}')]")
                    print(f"\nFound {len(elements)} elements containing '{keyword}' after tab switch:")
                    for i, element in enumerate(elements):
                        tag_name = element.tag_name
                        try:
                            element_text = element.text
                            element_class = element.get_attribute("class") or "no-class"
                            element_id = element.get_attribute("id") or "no-id"
                            is_displayed = element.is_displayed()
                            print(f"  {i+1}. <{tag_name}> - Text: '{element_text[:30]}{'...' if len(element_text) > 30 else ''}' - Class: {element_class}")
                            print(f"     ID: {element_id}, Displayed: {is_displayed}")
                        except Exception as e:
                            print(f"  {i+1}. <{tag_name}> - Error getting details: {str(e)}")
                print("--- END DEBUG ---\n")
            except Exception as e:
                print(f"Transcript tab not found or already active: {str(e)}. Proceeding...")
            
            print("Extracting transcript text from the page...")
            
            # Take a screenshot before extraction for debugging
            pre_extract_screenshot_path = os.path.join(screenshot_dir, f"before_extract_{video_id.replace('/', '_')}.png")
            driver.save_screenshot(pre_extract_screenshot_path)
            print(f"Screenshot before extraction saved to {pre_extract_screenshot_path}")
            
            # Try multiple methods to find and extract the transcript text
            transcript_text = ""
            extraction_successful = False
            
            # Method 1: Look for elements with transcript content
            print("Method 1: Looking for transcript container elements...")
            try:
                # Try to find transcript container with multiple possible selectors
                transcript_containers = driver.find_elements(By.XPATH, 
                    "//div[contains(@class, 'transcript') or contains(@class, 'captions')]//div | " +
                    "//div[starts-with(@id, 'transcript-') or starts-with(@id, 'captions-')] | " +
                    "//div[@role='tabpanel' and .//div[contains(text(), 'Transcript')]]//div")
                    
                if transcript_containers:
                    print(f"Found {len(transcript_containers)} potential transcript container elements")
                    
                    # Try to extract text from each container
                    for i, container in enumerate(transcript_containers):
                        try:
                            container_text = container.text.strip()
                            
                            # Check if this looks like transcript content (contains timestamps or multiple lines)
                            if container_text and len(container_text) > 50 and ('\n' in container_text or ':' in container_text):
                                print(f"Container {i+1} appears to have transcript content ({len(container_text)} chars)")
                                if len(container_text) > len(transcript_text):
                                    transcript_text = container_text
                                    extraction_successful = True
                            elif container_text:
                                print(f"Container {i+1} text is too short or doesn't look like transcript content: {container_text[:30]}...")
                        except Exception as e:
                            print(f"Error extracting text from container {i+1}: {str(e)}")
            except Exception as e:
                print(f"Method 1 failed: {str(e)}")
            
            # Method 2: Look for elements containing timestamps (which are common in transcripts)
            if not extraction_successful or not transcript_text:
                print("Method 2: Looking for elements containing timestamps...")
                try:
                    # Look for elements that might contain timestamps (HH:MM:SS or MM:SS format)
                    timestamp_elements = driver.find_elements(By.XPATH, 
                        "//div[contains(text(), ':') and string-length(normalize-space(text())) <= 8]/..")
                    
                    if timestamp_elements:
                        print(f"Found {len(timestamp_elements)} potential timestamp parent elements")
                        
                        # Find the parent container that might contain all transcripts
                        for i, element in enumerate(timestamp_elements):
                            try:
                                # Go up to a container that might hold multiple timestamps
                                parent = element.find_element(By.XPATH, "./..")
                                parent_text = parent.text.strip()
                                
                                if parent_text and len(parent_text) > 100 and '\n' in parent_text:
                                    print(f"Parent element {i+1} appears to have transcript content ({len(parent_text)} chars)")
                                    if len(parent_text) > len(transcript_text):
                                        transcript_text = parent_text
                                        extraction_successful = True
                            except Exception as e:
                                print(f"Error processing timestamp parent {i+1}: {str(e)}")
                except Exception as e:
                    print(f"Method 2 failed: {str(e)}")
            
            # Method 3: Try to find all text paragraphs that might be transcript lines
            if not extraction_successful or not transcript_text:
                print("Method 3: Looking for paragraphs of text...")
                try:
                    # Find elements that might be paragraphs of transcript text
                    paragraph_elements = driver.find_elements(By.CSS_SELECTOR, 
                        "div.transcript p, div.transcript div, div[role='tabpanel'] p, div[data-testid*='transcript'] div")
                    
                    if paragraph_elements:
                        print(f"Found {len(paragraph_elements)} potential paragraph elements")
                        
                        # Combine all paragraph texts
                        all_paragraphs = []
                        for i, element in enumerate(paragraph_elements):
                            try:
                                paragraph_text = element.text.strip()
                                if paragraph_text:
                                    all_paragraphs.append(paragraph_text)
                            except Exception as e:
                                print(f"Error processing paragraph {i+1}: {str(e)}")
                        
                        if all_paragraphs:
                            combined_text = "\n\n".join(all_paragraphs)
                            if len(combined_text) > len(transcript_text):
                                transcript_text = combined_text
                                extraction_successful = True
                                print(f"Extracted {len(all_paragraphs)} paragraphs of text ({len(transcript_text)} chars)")
                except Exception as e:
                    print(f"Method 3 failed: {str(e)}")
            
            # Method 4: Last resort - look for any text content within the transcript section
            if not extraction_successful or not transcript_text:
                print("Method 4: Looking for any text in the transcript section...")
                try:
                    # Try to find the transcript section and get all text
                    transcript_section = driver.find_element(By.XPATH, 
                        "//div[@role='tabpanel' and .//div[contains(text(), 'Transcript')]] | " +
                        "//section[contains(@class, 'transcript')] | " +
                        "//div[contains(@class, 'transcript-container')]")
                    
                    if transcript_section:
                        transcript_text = transcript_section.text.strip()
                        if transcript_text and len(transcript_text) > 50:
                            extraction_successful = True
                            print(f"Found transcript section with {len(transcript_text)} chars of text")
                except Exception as e:
                    print(f"Method 4 failed: {str(e)}")
            
            # Save the transcript to a file if extraction was successful
            if extraction_successful and transcript_text:
                print(f"Successfully extracted transcript text ({len(transcript_text)} characters)")
                
                # Clean up the video_id to use as filename
                clean_video_id = video_id.replace("https://www.loom.com/share/", "").replace("/", "_")
                
                # Function to sanitize file names
                def sanitize_filename(filename):
                    # Replace characters that are problematic in file paths
                    chars_to_replace = {
                        '/': '-',
                        '\\': '-',
                        ':': '-',
                        '*': '',
                        '?': '',
                        '"': "'",
                        '<': '(',
                        '>': ')',
                        '|': '-'
                    }
                    for char, replacement in chars_to_replace.items():
                        filename = filename.replace(char, replacement)
                    return filename
                
                # Get the video title from the page if possible
                try:
                    video_title = driver.title.replace(" - Loom", "").strip()
                    if not video_title:
                        video_title = clean_video_id
                except:
                    video_title = clean_video_id
                
                # Sanitize the video title for use in the filename
                video_title = sanitize_filename(video_title)
                
                # Create the output filename
                transcript_filename = f"{clean_video_id}.txt"
                if video_title and video_title != clean_video_id:
                    # Make sure the filename is sanitized again as a final check
                    safe_title = sanitize_filename(video_title)
                    transcript_filename = f"{safe_title} - {clean_video_id}.txt"

                # Further sanitize the complete filename as an extra precaution
                transcript_filename = sanitize_filename(transcript_filename)
                
                # Save to the download directory
                transcript_filepath = os.path.join(download_dir, transcript_filename)
                try:
                    with open(transcript_filepath, "w", encoding="utf-8") as f:
                        f.write(transcript_text)
                    print(f"Transcript saved to: {transcript_filepath}")
                    
                    # Take a screenshot after saving for debugging
                    after_save_screenshot_path = os.path.join(screenshot_dir, f"after_save_{video_id.replace('/', '_')}.png")
                    driver.save_screenshot(after_save_screenshot_path)
                    print(f"Screenshot after saving transcript saved to {after_save_screenshot_path}")
                except Exception as e:
                    print(f"Error saving transcript to file: {str(e)}")
            else:
                print("Failed to extract transcript text from the page")
                
                # Take a failure screenshot for debugging
                failure_screenshot_path = os.path.join(screenshot_dir, f"extraction_failed_{video_id.replace('/', '_')}.png")
                driver.save_screenshot(failure_screenshot_path)
                print(f"Failure screenshot saved to {failure_screenshot_path}")

            print(f"Processed video: {video_id}")
            with open(processed_file, "a") as f:
                f.write(f"{video_id}\n")
            # No longer removing videos one by one - will clear all at once after processing
            processed_videos.add(video_id)


        except TimeoutException:
            print(f"Timeout occurred while processing video {video_id}")
        except Exception as e:
            print(f"Error processing video {video_id}: {str(e)}")

        print("Waiting before next video...")
        time.sleep(5)

except Exception as e:
    print(f"An error occurred: {str(e)}")

finally:
    if driver:
        input("Press Enter to close the browser...")
        try:
            driver.quit()
        except WebDriverException:
            print("WebDriver was already closed.")
        except Exception as e:
            print(f"Error while closing the browser: {str(e)}")

    # Clean up the temporary directory
    import shutil

    shutil.rmtree(temp_dir, ignore_errors=True)
    print(f"Removed temporary Chrome profile directory: {temp_dir}")
    
    # Clear loom-videos.txt after all videos have been processed (unless --preserve is specified)
    if os.path.exists(input_file):
        if args.preserve:
            print(f"Input file '{input_file}' has been preserved. All successfully processed videos are recorded in '{processed_file}'.")
        else:
            with open(input_file, "w") as f:
                f.write("")  # Clear the file
            print(f"Input file '{input_file}' has been cleared. All successfully processed videos are recorded in '{processed_file}'.")
