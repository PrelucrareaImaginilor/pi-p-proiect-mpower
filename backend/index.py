from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import cv2 as cv
import numpy as np
import os
import glob
from collections import defaultdict
import math
import json
from dataclasses import dataclass
from typing import List, Dict
from tqdm import tqdm

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": "http://localhost:5173",
        "expose_headers": ["X-Vehicle-Stats"]
    }
})

@dataclass
class VehicleStats:
    id: int
    speeds: List[float]
    max_speed: float = 0
    avg_speed: float = 0

    def __init__(self, id: int):
        self.id = id
        self.speeds = []
        
    def update_speed(self, speed: float):
        if speed > 0:
            self.speeds.append(speed)
            self.max_speed = max(self.max_speed, speed)
            if self.speeds:
                self.avg_speed = sum(self.speeds) / len(self.speeds)

    def to_dict(self):
        return {
            "id": self.id,
            "max_speed": round(self.max_speed, 1),
            "avg_speed": round(self.avg_speed, 1)
        }

net = cv.dnn.readNet("models/yolov4.weights", "models/yolov4.cfg")
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

def clear_directory(directory):
    files = glob.glob(os.path.join(directory, '*'))
    for f in files:
        try:
            if os.path.isfile(f):
                os.remove(f)
        except Exception as e:
            print(f'Error: {e}')

def detect_vehicles(frame):
    height, width = frame.shape[:2]
    blob = cv.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)

    boxes = []
    confidences = []
    class_ids = []

    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5 and class_id == 2:  # class_id 2 for cars
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    indexes = cv.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
    return [boxes[i] for i in indexes]

def calculate_speed(prev_pos, curr_pos, fps):
    pixels_per_meter = 20
    
    dx = (curr_pos[0] - prev_pos[0]) / pixels_per_meter
    dy = (curr_pos[1] - prev_pos[1]) / pixels_per_meter
    distance = math.sqrt(dx*dx + dy*dy)
    time = 1/fps
    speed = distance/time * 3.6  # Convert to km/h
    return speed

@app.route('/process-video', methods=['POST'])
def process_video():
    try:
        if 'video' not       in request.files:
            return jsonify({"error": "No video file provided"}), 400

        clear_directory('input')
        clear_directory('output')

        video_file = request.files['video']
        input_path = os.path.join('input', video_file.filename)
        output_path = os.path.join('output', 'processed_' + video_file.filename)

        os.makedirs('input', exist_ok=True)
        os.makedirs('output', exist_ok=True)

        video_file.save(input_path)

        cap = cv.VideoCapture(input_path)
        fps = cap.get(cv.CAP_PROP_FPS)
        width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv.CAP_PROP_FRAME_COUNT))

        fourcc = cv.VideoWriter_fourcc(*'avc1')
        out = cv.VideoWriter(output_path, fourcc, fps, (width, height), isColor=True)

        prev_positions = {}
        vehicle_stats: Dict[int, VehicleStats] = {}
        next_vehicle_id = 0

        print(f"\nProcessing video: {video_file.filename}")
        print(f"Total frames: {total_frames}")

        for frame_idx in tqdm(range(total_frames), desc="Processing"):
            ret, frame = cap.read()
            if not ret:
                break

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
                    vehicle_stats[matching_id] = VehicleStats(matching_id)
                    speed = 0
                else:
                    speed = calculate_speed(prev_positions[matching_id], center, fps)
                    vehicle_stats[matching_id].update_speed(speed)

                prev_positions[matching_id] = center
                
                cv.rectangle(frame_copy, (x, y), (x + w, y + h), (0, 255, 0), 2)
                info_text = f"ID:{matching_id} - {speed:.1f} km/h"
                cv.putText(frame_copy, info_text, (x, y-10), 
                          cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            out.write(frame_copy)

        cap.release()
        out.release()

        stats = [v.to_dict() for v in vehicle_stats.values()]
        
        response = send_file(
            output_path,
            mimetype='video/mp4',
            as_attachment=True,
            download_name=f"processed_{video_file.filename}",
            conditional=True
        )
        
        response.headers['Access-Control-Expose-Headers'] = 'X-Vehicle-Stats'
        response.headers['X-Vehicle-Stats'] = json.dumps(stats)
        response.headers['Accept-Ranges'] = 'bytes'
        
        return response

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    for dir_name in ['input', 'output', 'models']:
        os.makedirs(dir_name, exist_ok=True)
    app.run(port=5000, debug=True)