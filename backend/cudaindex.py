import cv2 as cv
import numpy as np
import os
import math
import time
from tqdm import tqdm

def process_video(video_path):
    # Open video
    cap = cv.VideoCapture(video_path)
    total_frames = int(cap.get(cv.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv.CAP_PROP_FPS)
    
    # Storage for processed frames
    processed_frames = []
    
    # Tracking dictionaries
    prev_positions = {}
    vehicle_speeds = {}
    next_vehicle_id = 0

    # Process all frames first
    print("Processing video...")
    for frame_idx in tqdm(range(total_frames)):
        ret, frame = cap.read()
        if not ret:
            break

        # Detect and process vehicles
        boxes = detect_vehicles(frame)
        frame_copy = frame.copy()
        
        for box in boxes:
            x, y, w, h = box
            center = (x + w//2, y + h//2)
            
            min_dist = float('inf')
            matching_id = None
            
            for vid, prev_pos in prev_positions.items():
                dist = math.sqrt((center[0] - prev_pos[0])**2 + (center[1] - prev_pos[1])**2)
                if dist < min_dist and dist < 100:
                    min_dist = dist
                    matching_id = vid
            
            if matching_id is None:
                matching_id = next_vehicle_id
                next_vehicle_id += 1
                vehicle_speeds[matching_id] = 0
            else:
                speed = calculate_speed(prev_positions[matching_id], center, fps)
                vehicle_speeds[matching_id] = speed
            
            prev_positions[matching_id] = center
            
            # Draw annotations
            cv.rectangle(frame_copy, (x, y), (x + w, y + h), (0, 255, 0), 2)
            speed_text = f"{vehicle_speeds[matching_id]:.1f} km/h"
            cv.putText(frame_copy, speed_text, (x, y-10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        processed_frames.append(frame_copy)

    cap.release()
    
    print("\nProcessing complete! Playing video...")
    
    # Play processed video
    for frame in processed_frames:
        cv.imshow('Vehicle Detection', frame)
        key = cv.waitKey(int(1000/fps)) & 0xFF
        if key == ord('q') or key == 27:
            break
    
    cv.destroyAllWindows()

if __name__ == '__main__':
    video_path = 'recording.mp4'
    
    if not os.path.exists(video_path):
        print(f"Error: Video file not found at {video_path}")
    else:
        process_video(video_path)