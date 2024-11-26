import os
import time
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

COMPOSITE_API_URL = "http://127.0.0.1:8000/process_document"
DIRECTORY_TO_WATCH = "documents"

class DocumentHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith(".txt"):
            return

        try:
            with open(event.src_path, "r", encoding="utf-8") as file:
                text_content = file.read().strip()
            print(f"New file detected: {event.src_path}")

            data = {
                "documents": [text_content]
            }
            response = requests.post(COMPOSITE_API_URL, json=data)

            if response.status_code == 200:
                print(f"Document processed successfully: {response.json()}")
            else:
                print(f"Error processing document: {response.status_code} - {response.text}")
        
        except Exception as e:
            print(f"Error reading file {event.src_path}: {e}")

def start_watchdog():
    event_handler = DocumentHandler()
    observer = Observer()
    observer.schedule(event_handler, DIRECTORY_TO_WATCH, recursive=False)
    observer.start()
    print(f"Watching directory: {DIRECTORY_TO_WATCH}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    if not os.path.exists(DIRECTORY_TO_WATCH):
        os.makedirs(DIRECTORY_TO_WATCH)
    start_watchdog()
