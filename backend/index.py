from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import cv2 as cv
import numpy as np
import os
import glob

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

def clear_directory(directory):
    files = glob.glob(os.path.join(directory, '*'))
    for f in files:
        os.remove(f)

@app.route('/process-video', methods=['POST'])
def process_video():
    if 'video' not in request.files:
        return jsonify({"error": "No video file provided"}), 400

    # Clear input and output directories
    clear_directory('input')
    clear_directory('output')

    video_file = request.files['video']
    input_path = os.path.join('input', video_file.filename)
    output_path = os.path.join('output', 'processed_' + video_file.filename)

    video_file.save(input_path)

    # Process the video using OpenCV
    cap = cv.VideoCapture(input_path)
    fps = cap.get(cv.CAP_PROP_FPS)
    width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv.VideoWriter_fourcc(*'x264')
    out = cv.VideoWriter(output_path, fourcc, fps, (width, height), isColor=True)

    backSub = cv.createBackgroundSubtractorMOG2()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        fg_mask = backSub.apply(frame)
        contours, _ = cv.findContours(fg_mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        frame_out = frame.copy()
        for cnt in contours:
            if cv.contourArea(cnt) > 500:
                x, y, w, h = cv.boundingRect(cnt)
                cv.rectangle(frame_out, (x, y), (x + w, y + h), (0, 0, 200), 3)
        
        out.write(frame_out)
        

    cap.release()
    out.release()

    return send_file(output_path, as_attachment=True, mimetype='video/mp4')

if __name__ == '__main__':
    os.makedirs('input', exist_ok=True)
    os.makedirs('output', exist_ok=True)
    app.run(port=5000, debug=True)

    
  