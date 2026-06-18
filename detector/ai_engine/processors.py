import cv2
import os
from django.conf import settings
import numpy as np


def extract_frames(video_path, num_frames=15):
    """Extracts N frames evenly spaced throughout the video."""
    frames = []
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    if total_frames <= 0:
        return []

    # Calculate indices for even sampling (Beginning, Middle, End)
    indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)
    
    temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_frames')
    os.makedirs(temp_dir, exist_ok=True)

    for i, idx in enumerate(indices):
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        success, frame = cap.read()
        if success:
            frame_path = os.path.join(temp_dir, f"frame_{idx}.jpg")
            cv2.imwrite(frame_path, frame)
            frames.append(frame_path)
    
    cap.release()
    return frames