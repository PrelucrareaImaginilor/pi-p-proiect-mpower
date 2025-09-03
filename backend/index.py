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

# Enable OpenCV optimizations and set a reasonable thread count
cv.setUseOptimized(True)
try:
    cv.setNumThreads(max(1, os.cpu_count() - 1))
except Exception:
    # Some OpenCV builds/platforms may not support thread control
    pass

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
    # Reduce RANSAC iterations for faster estimation while keeping robustness
    M, inliers = cv.estimateAffinePartial2D(
        good0, good1,
                method=cv.RANSAC,
        ransacReprojThreshold=3.0,
        maxIters=100
    )
    return M, good0, good1, inliers


def stabilize_stream(cap, out, smooth_window=DEFAULT_SMOOTH_WINDOW, crop_ratio=DEFAULT_CROP, collect_transforms=False,
                     overlay=False, side_by_side=False, scale: float = 1.0):
    """Stabilize frames from cap writing to out. Optionally collect per-frame transforms.
    Returns list of dicts with raw & smoothed cumulative transforms if requested."""
    transforms = []  # raw cumulative (dx, dy, da)
    smooth_buf_dx = deque(maxlen=smooth_window)
    smooth_buf_dy = deque(maxlen=smooth_window)
    smooth_buf_da = deque(maxlen=smooth_window)
    # Running sums for O(1) moving averages
    sum_dx = 0.0
    sum_dy = 0.0
    sum_da = 0.0
    collected = []
    cam_path = []  # list of (sdx, sdy) for mini-map

    prev_gray = None
    cum_dx = cum_dy = cum_da = 0.0
    
    frame_index = 0
    # Pre-compute frame dimensions and crop indices once
    w = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
    do_crop = crop_ratio > 0.0
    if do_crop and w > 0 and h > 0:
        cx1 = int(w * crop_ratio)
        cy1 = int(h * crop_ratio)
        cx2 = w - cx1
        cy2 = h - cy1
    else:
        cx1 = cy1 = 0
        cx2 = w
        cy2 = h
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_index += 1
        if prev_gray is None:
            prev_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            if out is not None:
                out.write(frame)
            if collect_transforms:
                collected.append({"frame": frame_index, "dx": 0.0, "dy": 0.0, "da": 0.0,
                                   "sdx": 0.0, "sdy": 0.0, "sda": 0.0})
            continue
        
        gray_full = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        # Optionally downscale for faster motion estimation
        if 0.25 <= scale < 1.0:
            gray = cv.resize(gray_full, (int(w*scale), int(h*scale)), interpolation=cv.INTER_AREA)
            prev_for_est = cv.resize(prev_gray, (int(w*scale), int(h*scale)), interpolation=cv.INTER_AREA)
        else:
            gray = gray_full
            prev_for_est = prev_gray
        # Compute affine once per frame
        M, good0, good1, inliers = estimate_affine(prev_for_est, gray)
        if M is None:
            stabilized = frame  # fallback
            if collect_transforms:
                # reuse last smoothed if available
                if len(smooth_buf_dx) > 0:
                    sdx = sum_dx / len(smooth_buf_dx)
                    sdy = sum_dy / len(smooth_buf_dy)
                    sda = sum_da / len(smooth_buf_da)
                else:
                    sdx = cum_dx
                    sdy = cum_dy
                    sda = cum_da
                collected.append({"frame": frame_index, "dx": cum_dx, "dy": cum_dy, "da": cum_da,
                                   "sdx": sdx, "sdy": sdy, "sda": sda, "estimated": False})
        else:
            # If computed on downscaled frame, scale translations back
            scale_inv = 1.0 if scale >= 1.0 else (1.0/scale if scale >= 0.25 else 1.0)
            dx = M[0,2] * scale_inv; dy = M[1,2] * scale_inv
            da = math.atan2(M[1,0], M[0,0])
            cum_dx += dx; cum_dy += dy; cum_da += da
            # Maintain running sums for O(1) moving averages
            if len(smooth_buf_dx) == smooth_window:
                sum_dx -= smooth_buf_dx[0]
                sum_dy -= smooth_buf_dy[0]
                sum_da -= smooth_buf_da[0]
            smooth_buf_dx.append(cum_dx)
            smooth_buf_dy.append(cum_dy)
            smooth_buf_da.append(cum_da)
            sum_dx += cum_dx
            sum_dy += cum_dy
            sum_da += cum_da
            sdx = sum_dx / len(smooth_buf_dx)
            sdy = sum_dy / len(smooth_buf_dy)
            sda = sum_da / len(smooth_buf_da)
            # difference (high frequency component)
            diff_dx = sdx - cum_dx
            diff_dy = sdy - cum_dy
            diff_da = sda - cum_da
            cos_a = math.cos(diff_da); sin_a = math.sin(diff_da)
            M_adj = np.array([[cos_a, -sin_a, diff_dx],
                              [sin_a,  cos_a, diff_dy]], dtype=np.float32)
            stabilized = cv.warpAffine(frame, M_adj, (w, h), flags=cv.INTER_LINEAR, borderMode=cv.BORDER_REFLECT)
            if do_crop and w > 0 and h > 0:
                stabilized = stabilized[cy1:cy2, cx1:cx2]
                stabilized = cv.resize(stabilized, (w, h))
            if overlay:
                # Track smoothed path for mini-map
                cam_path.append((sdx, sdy))
            if overlay:
                # Draw feature correspondences (sample up to 200)
                if good0 is not None and good1 is not None:
                    for (x2,y2) in good1[:200].reshape(-1,2):
                        cv.circle(stabilized, (int(x2), int(y2)), 2, (0,255,255), -1, cv.LINE_AA)
                # Draw crop border
                if do_crop and w > 0 and h > 0:
                    m = int(w * crop_ratio); n = int(h * crop_ratio)
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
        if out is not None:
            if side_by_side:
                combo = np.hstack([frame, stabilized])
                out.write(combo)
            else:
                out.write(stabilized)
        prev_gray = gray_full
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
    os.makedirs('output', exist_ok=True)
    base = os.path.basename(input_path)
    # Select container/codec based on requested format with fallbacks
    fmt = (request.args.get('format') or 'mp4').lower()
    if fmt not in ('webm', 'mp4'):
        fmt = 'mp4'
    if fmt == 'webm':
        output_name = f"stabilized_{os.path.splitext(base)[0]}.webm"
        mimetype = 'video/webm'
        codec_candidates = ['VP80', 'VP90']  # VP8 then VP9
    else:
        output_name = f"stabilized_{base}"
        mimetype = 'video/mp4'
        codec_candidates = ['avc1', 'H264', 'mp4v']  # try H.264 then fallback to MPEG4
    output_path = os.path.join('output', output_name)
    # Determine if only JSON is requested to skip file writes
    only_json = request.args.get('json') == '1'
    out = None
    if not only_json:
        for cc in codec_candidates:
            try:
                fourcc_try = cv.VideoWriter_fourcc(*cc)
                out_try = cv.VideoWriter(output_path, fourcc_try, fps, (width, height), isColor=True)
                if out_try is not None and out_try.isOpened():
                    out = out_try
                    break
            except Exception:
                continue
        # Final fallback: default platform writer
        if out is None:
            fourcc_default = cv.VideoWriter_fourcc(*'mp4v')
            output_path = os.path.join('output', f"stabilized_{base}")
            mimetype = 'video/mp4'
            out = cv.VideoWriter(output_path, fourcc_default, fps, (width, height), isColor=True)

    try:
        smooth_window = int(request.args.get('window') or DEFAULT_SMOOTH_WINDOW)
        crop_ratio = float(request.args.get('crop') or DEFAULT_CROP)
        collect = request.args.get('stats') == '1' or request.args.get('json') == '1'
        overlay = request.args.get('overlay') == '1'
        side_by_side = request.args.get('sbs') == '1'
        scale = float(request.args.get('scale') or 1.0)
        if scale <= 0 or scale > 1:
            scale = 1.0
    except ValueError:
        return jsonify({"error": "Invalid numeric parameter"}), 400

    # Adjust output width if side_by_side
    if side_by_side and out is not None:
        out.release()
        # Recreate writer with same chosen codec and new size
        # Try to reuse the first successful codec
        recreated = False
        for cc in codec_candidates:
            try:
                fourcc_try = cv.VideoWriter_fourcc(*cc)
                out_try = cv.VideoWriter(output_path, fourcc_try, fps, (width*2, height), isColor=True)
                if out_try is not None and out_try.isOpened():
                    out = out_try
                    recreated = True
                    break
            except Exception:
                continue
        if not recreated:
            fourcc_default = cv.VideoWriter_fourcc(*'mp4v')
            out = cv.VideoWriter(output_path, fourcc_default, fps, (width*2, height), isColor=True)
            mimetype = 'video/mp4'

    stats = stabilize_stream(cap, out, smooth_window=smooth_window, crop_ratio=crop_ratio,
                              collect_transforms=collect, overlay=overlay, side_by_side=side_by_side, scale=scale)
    cap.release();
    
    if out is not None:
        out.release()

    if request.args.get('json') == '1':
        # Persist stats if available
        if stats is not None:
            try:
                os.makedirs('output', exist_ok=True)
                with open(os.path.join('output', f'{os.path.splitext(os.path.basename(output_path))[0]}_stats.json'), 'w', encoding='utf-8') as f:
                    json.dump(stats, f)
            except Exception:
                pass
        return jsonify({
            "video": base,
            "output": os.path.basename(output_path),
            "frames": 0 if stats is None else len(stats),
            "smooth_window": smooth_window,
            "crop_ratio": crop_ratio,
            "overlay": overlay,
            "side_by_side": side_by_side,
            "scale": scale,
            "transforms": stats or []
        })

    # Persist stats if requested/available even when returning video
    if stats is not None:
        try:
            with open(os.path.join('output', f'{os.path.splitext(os.path.basename(output_path))[0]}_stats.json'), 'w', encoding='utf-8') as f:
                json.dump(stats, f)
        except Exception:
            pass

    resp = send_file(output_path, as_attachment=False, mimetype=mimetype)
    resp.headers['X-Input-Video'] = base
    resp.headers['X-Smooth-Window'] = str(smooth_window)
    resp.headers['X-Crop-Ratio'] = f"{crop_ratio:.4f}"
    resp.headers['X-Overlay'] = '1' if overlay else '0'
    resp.headers['X-SideBySide'] = '1' if side_by_side else '0'
    resp.headers['X-Output-Video'] = os.path.basename(output_path)
    if stats is not None:
        resp.headers['X-Frames'] = str(len(stats))
    return resp


@app.get('/stats')
def get_stats():
    """Return previously persisted stats by output filename: /stats?output=stabilized_<file>.mp4"""
    output_name = request.args.get('output')
    if not output_name:
        return jsonify({"error": "Missing output query parameter"}), 400
    stats_path = os.path.join('output', f'{os.path.splitext(output_name)[0]}_stats.json')
    if not os.path.isfile(stats_path):
        return jsonify({"error": "Stats not found"}), 404
    try:
        with open(stats_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        return jsonify({"error": "Failed to read stats"}), 500
    return jsonify({
        "output": output_name,
        "frames": len(data) if isinstance(data, list) else 0,
        "transforms": data if isinstance(data, list) else []
    })

# Remove legacy duplicate route if present
@app.route('/process-video', methods=['POST'])
def legacy_endpoint():
    return jsonify({"error": "Deprecated. Use /stabilize-video endpoint.", "use": "/stabilize-video"}), 410

if __name__ == '__main__':
    os.makedirs('input', exist_ok=True)
    os.makedirs('output', exist_ok=True)
    app.run(port=5000, debug=True)


