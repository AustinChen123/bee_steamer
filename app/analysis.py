import cv2
import asyncio
import datetime
import json
import os
import numpy as np
from collections import defaultdict, deque

from app.websocket_server import connected_clients
from app.detect_bees_density import detect_bees_density

ALL_HIVES = {
    "Hive_1": (650, 400, 1000, 800),
    "Hive_2": (230, 400, 650, 700),
    "Hive_3": (700, 300, 1200, 550),
}

BACKGROUND_FRAMES = 15
ANALYSIS_INTERVAL = 15  # 單位秒
MOVING_AVERAGE_WINDOW = 3

BG_HIVE1_STATIC = cv2.imread("background_hive1.png", cv2.IMREAD_GRAYSCALE)
BG_HIVE23_STATIC = cv2.imread("background_hive23.png", cv2.IMREAD_GRAYSCALE)

# 過去數據緩衝區
bee_history = defaultdict(lambda: deque(maxlen=MOVING_AVERAGE_WINDOW))


async def build_background(cap, num_frames):
    frames = []
    for _ in range(num_frames):
        ret, frame = cap.read()
        if not ret:
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frames.append(gray)
        await asyncio.sleep(0.1)
    if not frames:
        return None
    return np.mean(frames, axis=0).astype(np.uint8)


async def analyze_every_interval(cap, hive_names, static_bg):
    while True:
        bg = await build_background(cap, BACKGROUND_FRAMES)
        if bg is None:
            bg = static_bg

        ret, frame = cap.read()
        if not ret:
            await asyncio.sleep(ANALYSIS_INTERVAL)
            continue

        result = {}
        for name in hive_names:
            x1, y1, x2, y2 = ALL_HIVES[name]
            roi_frame = frame[y1:y2, x1:x2]
            roi_bg = bg[y1:y2, x1:x2]

            count = detect_bees_density(
                roi_frame, roi_bg, hive_id=name, debug=True)
            bee_history[name].append(count)
            smooth_count = int(np.mean(bee_history[name]))
            result[name] = smooth_count

        result["timestamp"] = datetime.datetime.utcnow().isoformat()
        msg = json.dumps(result)
        await asyncio.gather(*[ws.send(msg) for ws in connected_clients])

        await asyncio.sleep(ANALYSIS_INTERVAL)
