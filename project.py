import os
import time
import whisper
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

# Define supported file formats
SUPPORTED_FORMATS = {".mp3", ".wav", ".mp4", ".mkv", ".mov", ".flv", ".aac", ".m4a"}

# Load Whisper model
model = whisper.load_model("small") 

# Function to transcribe audio/video files
def transcribe_file(file_path):
    try:
        logging.info(f"Processing: {file_path}")
        result = model.transcribe(file_path)

        # Save transcription to a text file
        transcript_path = Path(file_path).with_suffix(".txt")
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(result["text"])
        
        logging.info(f"Transcription saved: {transcript_path}")
    except Exception as e:
        logging.error(f"Error processing {file_path}: {e}")

# Function to recursively scan directories
def scan_directory(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if Path(file).suffix.lower() in SUPPORTED_FORMATS:
                transcribe_file(file_path)

# File monitoring class
class FileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and Path(event.src_path).suffix.lower() in SUPPORTED_FORMATS:
            transcribe_file(event.src_path)

# Function to monitor directory for new files
def monitor_directory(directory):
    event_handler = FileHandler()
    observer = Observer()
    observer.schedule(event_handler, directory, recursive=True)
    observer.start()
    
    logging.info(f"Monitoring folder: {directory}")
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        observer.stop()
    
    observer.join()

# Main execution
if __name__ == "__main__":
    folder_path = "D:\p_sample" 

    # Ensure directory exists
    Path(folder_path).mkdir(parents=True, exist_ok=True)

    # Perform an initial scan
    scan_directory(folder_path)

    # Start real-time monitoring
    monitor_directory(folder_path)