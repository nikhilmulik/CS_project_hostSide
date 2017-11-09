import time  
import sys
import requests
# pip install watchdog
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler


class MyHandler(PatternMatchingEventHandler):
    """
    python watch_for_changes.py path\to\image\directory
    """
    patterns = ["*.png", "*.jpeg"]

    def process(self, event):
        # print event.src_path, event.event_type
        if event.event_type == 'modified':
            url = 'http://localhost:5000/update_webcam_capture/'
            files = {'media': open(event.src_path, 'rb')}
            requests.post(url, files=files)


if __name__ == '__main__':
    args = sys.argv[1:]
    observer = Observer()
    observer.schedule(MyHandler(), path=args[0] if args else '.')
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
