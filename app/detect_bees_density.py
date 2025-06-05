import cv2
import numpy as np
import os
from scipy.ndimage import gaussian_filter, maximum_filter


def detect_bees_density(frame, background, hive_id="hive", debug=False):
    gray = cv2.cvtColor(
        frame, cv2.COLOR_BGR2GRAY) if frame.ndim == 3 else frame
    bg_gray = cv2.cvtColor(
        background, cv2.COLOR_BGR2GRAY) if background.ndim == 3 else background

    diff = cv2.absdiff(gray, bg_gray)
    _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
    thresh = cv2.dilate(thresh, None, iterations=1)

    # 高斯模糊產生密度圖
    density = gaussian_filter(thresh.astype(np.float32), sigma=5)

    # 峰值點判斷
    local_max = maximum_filter(density, size=15) == density
    detected_peaks = np.logical_and(local_max, density > 50)
    bee_count = np.count_nonzero(detected_peaks)

    if debug:
        os.makedirs(f"debug_output/{hive_id}", exist_ok=True)
        cv2.imwrite(f"debug_output/{hive_id}/01_diff.jpg", diff)
        cv2.imwrite(f"debug_output/{hive_id}/02_thresh.jpg", thresh)
        density_norm = cv2.normalize(density, None, 0, 255, cv2.NORM_MINMAX)
        cv2.imwrite(
            f"debug_output/{hive_id}/03_density.jpg", density_norm.astype(np.uint8))
        peaks_vis = frame.copy()
        ys, xs = np.where(detected_peaks)
        for x, y in zip(xs, ys):
            cv2.circle(peaks_vis, (x, y), 4, (0, 0, 255), -1)
        cv2.imwrite(f"debug_output/{hive_id}/04_peaks.jpg", peaks_vis)

    return bee_count
