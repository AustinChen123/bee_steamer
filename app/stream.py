import subprocess
import cv2

def get_stream_url(youtube_url):
    result = subprocess.run(
        ["yt-dlp", "-g", youtube_url],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        check=True
    )
    return result.stdout.strip()

def open_stream(url):
    cap = cv2.VideoCapture(url)
    if not cap.isOpened():
        raise RuntimeError("無法開啟串流")
    return cap
