from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import cv2 as cv
import numpy as np
import os
import math
from collections import deque
import json

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

# ---------------- Generic Video Stabilization Only -----------------
# Configuration defaults (can be overridden per request via query params)
DEFAULT_SMOOTH_WINDOW = 10      # moving average length over cumulative transforms
MAX_FEATURES = 500
QUALITY_LEVEL = 0.01
MIN_DISTANCE = 20
DEFAULT_CROP = 0.04             # 4% border crop to hide warping edges
# New defaults
DEFAULT_OVERLAY = False


def estimate_affine(prev_gray, gray):
    pts0 = cv.goodFeaturesToTrack(prev_gray, maxCorners=MAX_FEATURES,
                                  qualityLevel=QUALITY_LEVEL,
                                  minDistance=MIN_DISTANCE, blockSize=3)
    if pts0 is None or len(pts0) < 8:
        return None, None, None, None
    pts1, st, _ = cv.calcOpticalFlowPyrLK(prev_gray, gray, pts0, None,
                                          winSize=(21,21), maxLevel=3,
                                          criteria=(cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 30, 0.01))
    if pts1 is None:
        return None, None, None, None
    st = st.reshape(-1)
    good0 = pts0[st == 1]
    good1 = pts1[st == 1]
    if len(good0) < 8:
        return None, None, None, None
    M, inliers = cv.estimateAffinePartial2D(good0, good1, method=cv.RANSAC, ransacReprojThreshold=3.0, maxIters=200)
    return M, good0, good1, inliers


def stabilize_stream(cap, out, smooth_window=DEFAULT_SMOOTH_WINDOW, crop_ratio=DEFAULT_CROP, collect_transforms=False,
                     overlay=False, side_by_side=False):
    """Stabilize frames from cap writing to out. Optionally collect per-frame transforms.
    Returns list of dicts with raw & smoothed cumulative transforms if requested."""
    transforms = []  # raw cumulative (dx, dy, da)
    smooth_buf_dx = deque(maxlen=smooth_window)
    smooth_buf_dy = deque(maxlen=smooth_window)
    smooth_buf_da = deque(maxlen=smooth_window)
    collected = []
    cam_path = []  # list of (sdx, sdy) for mini-map

    prev_frame = None
    prev_gray = None
    cum_dx = cum_dy = cum_da = 0.0

    frame_index = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_index += 1
        if prev_gray is None:
            prev_frame = frame.copy()
            prev_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            out.write(frame)
            if collect_transforms:
                collected.append({"frame": frame_index, "dx": 0.0, "dy": 0.0, "da": 0.0,
                                   "sdx": 0.0, "sdy": 0.0, "sda": 0.0})
            continue

        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        M = estimate_affine(prev_gray, gray)[0] if not overlay else None
        # Recompute with features if overlay needed
        if overlay:
            M, good0, good1, inliers = estimate_affine(prev_gray, gray)
        if M is None:
            stabilized = frame  # fallback
            if collect_transforms:
                # reuse last smoothed if available
                sdx = float(np.mean(smooth_buf_dx)) if smooth_buf_dx else cum_dx
                sdy = float(np.mean(smooth_buf_dy)) if smooth_buf_dy else cum_dy
                sda = float(np.mean(smooth_buf_da)) if smooth_buf_da else cum_da
                collected.append({"frame": frame_index, "dx": cum_dx, "dy": cum_dy, "da": cum_da,
                                   "sdx": sdx, "sdy": sdy, "sda": sda, "estimated": False})
        else:
            dx = M[0,2]; dy = M[1,2]
            da = math.atan2(M[1,0], M[0,0])
            cum_dx += dx; cum_dy += dy; cum_da += da
            smooth_buf_dx.append(cum_dx)
            smooth_buf_dy.append(cum_dy)
            smooth_buf_da.append(cum_da)
            sdx = float(np.mean(smooth_buf_dx))
            sdy = float(np.mean(smooth_buf_dy))
            sda = float(np.mean(smooth_buf_da))
            # difference (high frequency component)
            diff_dx = sdx - cum_dx
            diff_dy = sdy - cum_dy
            diff_da = sda - cum_da
            cos_a = math.cos(diff_da); sin_a = math.sin(diff_da)
            M_adj = np.array([[cos_a, -sin_a, diff_dx],
                              [sin_a,  cos_a, diff_dy]], dtype=np.float32)
            h, w = frame.shape[:2]
            stabilized = cv.warpAffine(frame, M_adj, (w, h), flags=cv.INTER_LINEAR, borderMode=cv.BORDER_REFLECT)
            if crop_ratio > 0:
                cx1 = int(w*crop_ratio); cy1 = int(h*crop_ratio)
                cx2 = w - cx1; cy2 = h - cy1
                stabilized = stabilized[cy1:cy2, cx1:cx2]
                stabilized = cv.resize(stabilized, (w, h))
            if overlay:
                # Draw feature correspondences (sample up to 200)
                if good0 is not None and good1 is not None:
                    for (x2,y2) in good1[:200].reshape(-1,2):
                        cv.circle(stabilized, (int(x2), int(y2)), 2, (0,255,255), -1, cv.LINE_AA)
                # Draw crop border
                if crop_ratio > 0:
                    m = int(w*crop_ratio); n = int(h*crop_ratio)
                    cv.rectangle(stabilized, (m,n), (w-m, h-n), (0,200,0), 1, cv.LINE_AA)
                # Mini camera path panel
                if len(cam_path) > 2:
                    panel_h, panel_w = 120, 180
                    panel = np.zeros((panel_h, panel_w, 3), dtype=np.uint8)
                    xs = [p[0] for p in cam_path]; ys = [p[1] for p in cam_path]
                    min_x, max_x = min(xs), max(xs)
                    min_y, max_y = min(ys), max(ys)
                    span_x = max(1e-6, max_x - min_x)
                    span_y = max(1e-6, max_y - min_y)
                    pts_panel = []
                    for px, py in cam_path:
                        nx = int((px - min_x)/span_x * (panel_w-10) + 5)
                        ny = int((py - min_y)/span_y * (panel_h-10) + 5)
                        pts_panel.append((nx, ny))
                    for i in range(1, len(pts_panel)):
                        cv.line(panel, pts_panel[i-1], pts_panel[i], (255,255,0), 1, cv.LINE_AA)
                    cv.putText(panel, 'Path', (5,15), cv.FONT_HERSHEY_SIMPLEX, 0.45,(255,255,255),1,cv.LINE_AA)
                    # Place panel top-left
                    ph, pw = panel.shape[:2]
                    stabilized[5:5+ph, 5:5+pw] = cv.addWeighted(stabilized[5:5+ph, 5:5+pw], 0.4, panel, 0.6, 0)
                # Text stats
                cv.putText(stabilized, f"dx:{diff_dx:+.1f} dy:{diff_dy:+.1f}", (10, h-40), cv.FONT_HERSHEY_SIMPLEX, 0.5,(0,200,255),1,cv.LINE_AA)
                cv.putText(stabilized, f"ang:{math.degrees(diff_da):+.2f} deg", (10, h-20), cv.FONT_HERSHEY_SIMPLEX, 0.5,(0,200,255),1,cv.LINE_AA)
        if side_by_side:
            combo = np.hstack([prev_frame if prev_frame is not None else frame, stabilized])
            out.write(combo)
        else:
            out.write(stabilized)
        prev_gray = gray
        prev_frame = frame
    return collected if collect_transforms else None

# ---------------- API Endpoints -----------------

@app.route('/stabilize-video', methods=['POST'])
def stabilize_video():
    """Upload a video (field name 'video') OR specify ?filename= existing file in ./input.
    Returns stabilized video unless ?json=1 provided (then returns only transform stats JSON).
    Query params:
      window=<int> smoothing window (default 10)
      crop=<float> border crop ratio (default 0.04)
      stats=1 to include transform stats (ignored if json=1 which always returns stats)
    """
    filename_param = request.args.get('filename')
    input_path = None

    if 'video' in request.files:
        os.makedirs('input', exist_ok=True)
        up = request.files['video']
        input_path = os.path.join('input', up.filename)
        up.save(input_path)
    elif filename_param:
        cand = os.path.join('input', filename_param)
        if not os.path.isfile(cand):
            return jsonify({"error": f"File not found: {filename_param}"}), 404
        input_path = cand
    else:
        return jsonify({"error": "Provide a video file or ?filename= existing in /input"}), 400

    cap = cv.VideoCapture(input_path)
    if not cap.isOpened():
        return jsonify({"error": f"Cannot open video: {input_path}"}), 500

    fps = cap.get(cv.CAP_PROP_FPS) or 25
    width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv.VideoWriter_fourcc(*'mp4v')
    os.makedirs('output', exist_ok=True)
    base = os.path.basename(input_path)
    output_path = os.path.join('output', f'stabilized_{base}')
    out = cv.VideoWriter(output_path, fourcc, fps, (width, height), isColor=True)

    try:
        smooth_window = int(request.args.get('window') or DEFAULT_SMOOTH_WINDOW)
        crop_ratio = float(request.args.get('crop') or DEFAULT_CROP)
        collect = request.args.get('stats') == '1' or request.args.get('json') == '1'
        overlay = request.args.get('overlay') == '1'
        side_by_side = request.args.get('sbs') == '1'
    except ValueError:
        return jsonify({"error": "Invalid numeric parameter"}), 400

    # Adjust output width if side_by_side
    if side_by_side:
        out.release()
        fourcc = cv.VideoWriter_fourcc(*'mp4v')
        out = cv.VideoWriter(output_path, fourcc, fps, (width*2, height), isColor=True)

    stats = stabilize_stream(cap, out, smooth_window=smooth_window, crop_ratio=crop_ratio,
                              collect_transforms=collect, overlay=overlay, side_by_side=side_by_side)
    cap.release(); out.release()

    if request.args.get('json') == '1':
        return jsonify({
            "video": base,
            "output": os.path.basename(output_path),
            "frames": 0 if stats is None else len(stats),
            "smooth_window": smooth_window,
            "crop_ratio": crop_ratio,
            "overlay": overlay,
            "side_by_side": side_by_side,
            "transforms": stats or []
        })

    resp = send_file(output_path, as_attachment=True, mimetype='video/mp4')
    resp.headers['X-Input-Video'] = base
    resp.headers['X-Smooth-Window'] = str(smooth_window)
    resp.headers['X-Crop-Ratio'] = f"{crop_ratio:.4f}"
    resp.headers['X-Overlay'] = '1' if overlay else '0'
    resp.headers['X-SideBySide'] = '1' if side_by_side else '0'
    if stats is not None:
        resp.headers['X-Frames'] = str(len(stats))
    return resp

# Remove legacy duplicate route if present
@app.route('/process-video', methods=['POST'])
def legacy_endpoint():
    return jsonify({"error": "Deprecated. Use /stabilize-video endpoint.", "use": "/stabilize-video"}), 410

if __name__ == '__main__':
    os.makedirs('input', exist_ok=True)
    os.makedirs('output', exist_ok=True)
    app.run(port=5000, debug=True)


