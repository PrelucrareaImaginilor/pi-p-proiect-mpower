

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import cv2 as cv
import numpy as np
import os
import math
from collections import deque
import json
import time, csv
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

cv.setUseOptimized(True)
try:
    cv.setNumThreads(max(1, os.cpu_count() - 1))
except Exception:
    pass

DEFAULT_SMOOTH_WINDOW = 10      # moving average length over cumulative transforms
MAX_FEATURES = 500
QUALITY_LEVEL = 0.01
MIN_DISTANCE = 20
DEFAULT_CROP = 0.04             # 4% border crop to hide warping edges
DEFAULT_OVERLAY = False

LOG_CSV_PATH = os.path.join('output', 'stabilization_runs.csv')


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
    M, inliers = cv.estimateAffinePartial2D(
        good0, good1,
                method=cv.RANSAC,
        ransacReprojThreshold=3.0,
        maxIters=100
    )
    return M, good0, good1, inliers


def estimate_homography(prev_gray, gray, ratio_thresh=0.75):
    orb = cv.ORB_create(nfeatures=MAX_FEATURES)
    kp1, des1 = orb.detectAndCompute(prev_gray, None)
    kp2, des2 = orb.detectAndCompute(gray, None)
    
    if des1 is None or des2 is None or len(des1) < 8 or len(des2) < 8:
        return None, None, None
    
    bf = cv.BFMatcher(cv.NORM_HAMMING, crossCheck=False)
    matches = bf.knnMatch(des1, des2, k=2)
    
    good_matches = []
    for m, n in matches:
        if m.distance < ratio_thresh * n.distance:
            good_matches.append(m)
    
    if len(good_matches) < 8:
        return None, None, None
    
    pts1 = np.float32([kp1[m.queryIdx].pt for m in good_matches])
    pts2 = np.float32([kp2[m.trainIdx].pt for m in good_matches])
    
    H, mask = cv.findHomography(pts1, pts2, cv.RANSAC, 5.0)
    
    if H is None:
        return None, None, None
    
    dx = H[0, 2] / H[2, 2] if H[2, 2] != 0 else 0
    dy = H[1, 2] / H[2, 2] if H[2, 2] != 0 else 0
    da = math.atan2(H[1, 0], H[0, 0])
    
    return H, pts1[mask.ravel()==1], pts2[mask.ravel()==1]


def smooth_trajectory(trajectory, radius):
    if len(trajectory) < radius:
        return trajectory
    
    smoothed = []
    kernel = cv.getGaussianKernel(2*radius+1, -1).flatten()
    
    for i in range(len(trajectory)):
        start = max(0, i - radius)
        end = min(len(trajectory), i + radius + 1)
        window = trajectory[start:end]
        weights = kernel[radius - (i - start): radius + (end - i)]
        weights = weights / np.sum(weights)
        
        smoothed_dx = np.sum([w * t['dx'] for w, t in zip(weights, window)])
        smoothed_dy = np.sum([w * t['dy'] for w, t in zip(weights, window)])
        smoothed_da = np.sum([w * t['da'] for w, t in zip(weights, window)])
        
        smoothed.append({
            'dx': smoothed_dx,
            'dy': smoothed_dy,
            'da': smoothed_da
        })
    
    return smoothed


def stabilize_stream(cap, out, smooth_window=DEFAULT_SMOOTH_WINDOW, crop_ratio=DEFAULT_CROP, collect_transforms=False,
                     overlay=False, side_by_side=False, scale: float = 1.0):
    """Stabilize frames from cap writing to out. Optionally collect per-frame transforms + feature stats."""
    transforms = []  # raw cumulative (dx, dy, da) (kept for potential future use)
    smooth_buf_dx = deque(maxlen=smooth_window)
    smooth_buf_dy = deque(maxlen=smooth_window)
    smooth_buf_da = deque(maxlen=smooth_window)
    sum_dx = 0.0; sum_dy = 0.0; sum_da = 0.0
    collected = []
    cam_path = []  # list of (sdx, sdy) for mini-map

    prev_gray = None
    cum_dx = cum_dy = cum_da = 0.0

    raw_dx_increments = []  # per-frame raw increments
    raw_dy_increments = []
    raw_da_increments = []
    sm_dx_increments = []   # per-frame smoothed increments
    sm_dy_increments = []
    sm_da_increments = []

    fallback_frames = 0
    feature_counts = []
    inlier_counts = []

    frame_index = 0
    w = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
    do_crop = crop_ratio > 0.0
    if do_crop and w > 0 and h > 0:
        cx1 = int(w * crop_ratio); cy1 = int(h * crop_ratio)
        cx2 = w - cx1; cy2 = h - cy1
    else:
        cx1 = cy1 = 0; cx2 = w; cy2 = h
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
                                   "sdx": 0.0, "sdy": 0.0, "sda": 0.0,
                                   "features": 0, "inliers": 0, "inlier_ratio": 0.0, "estimated": False})
            continue

        gray_full = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        if 0.25 <= scale < 1.0:
            gray = cv.resize(gray_full, (int(w*scale), int(h*scale)), interpolation=cv.INTER_AREA)
            prev_for_est = cv.resize(prev_gray, (int(w*scale), int(h*scale)), interpolation=cv.INTER_AREA)
        else:
            gray = gray_full
            prev_for_est = prev_gray

        M, good0, good1, inliers = estimate_affine(prev_for_est, gray)
        if M is None:
            fallback_frames += 1
            stabilized = frame  # fallback (copy frame)
            if collect_transforms:
                if len(smooth_buf_dx) > 0:
                    sdx = sum_dx / len(smooth_buf_dx)
                    sdy = sum_dy / len(smooth_buf_dy)
                    sda = sum_da / len(smooth_buf_da)
                else:
                    sdx = cum_dx; sdy = cum_dy; sda = cum_da
                collected.append({"frame": frame_index, "dx": cum_dx, "dy": cum_dy, "da": cum_da,
                                   "sdx": sdx, "sdy": sdy, "sda": sda,
                                   "features": 0, "inliers": 0, "inlier_ratio": 0.0,
                                   "estimated": False})
        else:
            scale_inv = 1.0 if scale >= 1.0 else (1.0/scale if scale >= 0.25 else 1.0)
            dx = M[0,2] * scale_inv; dy = M[1,2] * scale_inv
            da = math.atan2(M[1,0], M[0,0])
            cum_dx += dx; cum_dy += dy; cum_da += da
            raw_dx_increments.append(dx)
            raw_dy_increments.append(dy)
            raw_da_increments.append(da)
            if len(smooth_buf_dx) == smooth_window:
                sum_dx -= smooth_buf_dx[0]; sum_dy -= smooth_buf_dy[0]; sum_da -= smooth_buf_da[0]
            smooth_buf_dx.append(cum_dx); smooth_buf_dy.append(cum_dy); smooth_buf_da.append(cum_da)
            sum_dx += cum_dx; sum_dy += cum_dy; sum_da += cum_da
            sdx = sum_dx / len(smooth_buf_dx); sdy = sum_dy / len(smooth_buf_dy); sda = sum_da / len(smooth_buf_da)
            # smoothed incremental (difference vs previous smoothed cumulative)
            if len(collected) > 0:
                prev_sdx = collected[-1]['sdx']; prev_sdy = collected[-1]['sdy']; prev_sda = collected[-1]['sda']
                sm_dx_increments.append(sdx - prev_sdx)
                sm_dy_increments.append(sdy - prev_sdy)
                sm_da_increments.append(sda - prev_sda)
            diff_dx = sdx - cum_dx; diff_dy = sdy - cum_dy; diff_da = sda - cum_da
            cos_a = math.cos(diff_da); sin_a = math.sin(diff_da)
            M_adj = np.array([[cos_a, -sin_a, diff_dx], [sin_a,  cos_a, diff_dy]], dtype=np.float32)
            stabilized = cv.warpAffine(frame, M_adj, (w, h), flags=cv.INTER_LINEAR, borderMode=cv.BORDER_REFLECT)
            if do_crop and w > 0 and h > 0:
                stabilized = stabilized[cy1:cy2, cx1:cx2]
                stabilized = cv.resize(stabilized, (w, h))
            if overlay:
                cam_path.append((sdx, sdy))
            if overlay:
                if good0 is not None and good1 is not None:
                    for (x2,y2) in good1[:200].reshape(-1,2):
                        cv.circle(stabilized, (int(x2), int(y2)), 2, (0,255,255), -1, cv.LINE_AA)
                if do_crop and w > 0 and h > 0:
                    m = int(w * crop_ratio); n = int(h * crop_ratio)
                    cv.rectangle(stabilized, (m,n), (w-m, h-n), (0,200,0), 1, cv.LINE_AA)
                if len(cam_path) > 2:
                    panel_h, panel_w = 120, 180
                    panel = np.zeros((panel_h, panel_w, 3), dtype=np.uint8)
                    xs = [p[0] for p in cam_path]; ys = [p[1] for p in cam_path]
                    min_x, max_x = min(xs), max(xs); min_y, max_y = min(ys), max(ys)
                    span_x = max(1e-6, max_x - min_x); span_y = max(1e-6, max_y - min_y)
                    pts_panel = []
                    for px, py in cam_path:
                        nx = int((px - min_x)/span_x * (panel_w-10) + 5)
                        ny = int((py - min_y)/span_y * (panel_h-10) + 5)
                        pts_panel.append((nx, ny))
                    for i in range(1, len(pts_panel)):
                        cv.line(panel, pts_panel[i-1], pts_panel[i], (255,255,0), 1, cv.LINE_AA)
                    cv.putText(panel, 'Path', (5,15), cv.FONT_HERSHEY_SIMPLEX, 0.45,(255,255,255),1,cv.LINE_AA)
                    ph, pw = panel.shape[:2]
                    stabilized[5:5+ph, 5:5+pw] = cv.addWeighted(stabilized[5:5+ph, 5:5+pw], 0.4, panel, 0.6, 0)
                cv.putText(stabilized, f"dx:{diff_dx:+.1f} dy:{diff_dy:+.1f}", (10, h-40), cv.FONT_HERSHEY_SIMPLEX, 0.5,(0,200,255),1,cv.LINE_AA)
                cv.putText(stabilized, f"ang:{math.degrees(diff_da):+.2f} deg", (10, h-20), cv.FONT_HERSHEY_SIMPLEX, 0.5,(0,200,255),1,cv.LINE_AA)
            # Feature / inlier stats
            features_cnt = int(len(good0)) if good0 is not None else 0
            inliers_cnt = int(inliers.sum()) if inliers is not None else 0
            inlier_ratio = (inliers_cnt / features_cnt * 100.0) if features_cnt > 0 else 0.0
            feature_counts.append(features_cnt)
            inlier_counts.append(inliers_cnt)
            if collect_transforms:
                collected.append({"frame": frame_index, "dx": cum_dx, "dy": cum_dy, "da": cum_da,
                                   "sdx": sdx, "sdy": sdy, "sda": sda,
                                   "features": features_cnt, "inliers": inliers_cnt,
                                   "inlier_ratio": inlier_ratio, "estimated": True})
        if out is not None:
            if side_by_side:
                combo = np.hstack([frame, stabilized])
                out.write(combo)
            else:
                out.write(stabilized)
        prev_gray = gray_full
    # Attach summary arrays for later metric computation
    return collected if collect_transforms else None

# --- Metrics & logging helpers -------------------------------------------------

def compute_summary_metrics(stats_list):
    if not stats_list or len(stats_list) <= 1:
        return {}
    # Exclude first frame (baseline) for motion stats
    cum_dx = [s['dx'] for s in stats_list]
    cum_dy = [s['dy'] for s in stats_list]
    cum_da = [s['da'] for s in stats_list]
    cum_sdx = [s['sdx'] for s in stats_list]
    cum_sdy = [s['sdy'] for s in stats_list]
    cum_sda = [s['sda'] for s in stats_list]
    raw_dx_inc = [cum_dx[i]-cum_dx[i-1] for i in range(1,len(cum_dx))]
    raw_dy_inc = [cum_dy[i]-cum_dy[i-1] for i in range(1,len(cum_dy))]
    raw_da_inc = [cum_da[i]-cum_da[i-1] for i in range(1,len(cum_da))]
    sm_dx_inc = [cum_sdx[i]-cum_sdx[i-1] for i in range(1,len(cum_sdx))]
    sm_dy_inc = [cum_sdy[i]-cum_sdy[i-1] for i in range(1,len(cum_sdy))]
    sm_da_inc = [cum_sda[i]-cum_sda[i-1] for i in range(1,len(cum_sda))]
    def std(a):
        if len(a) < 2: return 0.0
        m = sum(a)/len(a)
        return math.sqrt(sum((x-m)**2 for x in a)/(len(a)-1))
    raw_j_dx = std(raw_dx_inc); raw_j_dy = std(raw_dy_inc); raw_j_da = std(raw_da_inc)
    sm_j_dx = std(sm_dx_inc); sm_j_dy = std(sm_dy_inc); sm_j_da = std(sm_da_inc)
    def pct_reduction(raw, sm):
        return (100.0*(1 - sm/raw)) if raw > 1e-9 else 0.0
    reduction_dx = pct_reduction(raw_j_dx, sm_j_dx)
    reduction_dy = pct_reduction(raw_j_dy, sm_j_dy)
    reduction_da = pct_reduction(raw_j_da, sm_j_da)
    # Feature stats
    feat_vals = [s['features'] for s in stats_list if s.get('features',0) > 0]
    inl_vals = [s['inliers'] for s in stats_list if s.get('features',0) > 0]
    avg_features = sum(feat_vals)/len(feat_vals) if feat_vals else 0.0
    avg_inliers = sum(inl_vals)/len(inl_vals) if inl_vals else 0.0
    inlier_ratio_pct = (avg_inliers/avg_features*100.0) if avg_features>0 else 0.0
    fallback_frames = sum(1 for s in stats_list if not s.get('estimated', False))
    fallback_pct = (fallback_frames/len(stats_list))*100.0
    return {
        'frames': len(stats_list),
        'avg_features': avg_features,
        'avg_inliers': avg_inliers,
        'inlier_ratio_pct': inlier_ratio_pct,
        'fallback_pct': fallback_pct,
        'raw_jitter_dx': raw_j_dx,
        'raw_jitter_dy': raw_j_dy,
        'raw_jitter_rot_deg': math.degrees(raw_j_da),
        'stab_jitter_dx': sm_j_dx,
        'stab_jitter_dy': sm_j_dy,
        'stab_jitter_rot_deg': math.degrees(sm_j_da),
        'reduction_dx_pct': reduction_dx,
        'reduction_dy_pct': reduction_dy,
        'reduction_rot_pct': reduction_da
    }

def build_observation(m):
    if not m: return ''
    obs = []
    if m['fallback_pct'] > 15: obs.append('fallback frecvent / lumină slabă')
    if m['avg_features'] < 80: obs.append('puține trăsături (blur / zgomot)')
    if m['inlier_ratio_pct'] < 40: obs.append('aliniere dificilă')
    if m['reduction_dx_pct'] < 30 and m['reduction_dy_pct'] < 30: obs.append('scădere mică jitter (deja stabil)')
    if not obs: return 'stabilizare reușită'
    return '; '.join(obs)

def append_run_log(csv_path, row_dict):
    header = [
        'timestamp','video','resolution','duration_s','input_fps','proc_fps','frames',
        'smooth_window','crop','overlay','side_by_side','scale',
        'avg_features','avg_inliers','inlier_ratio_pct','fallback_pct',
        'raw_jitter_dx','stab_jitter_dx','reduction_dx_pct',
        'raw_jitter_dy','stab_jitter_dy','reduction_dy_pct',
        'raw_jitter_rot_deg','stab_jitter_rot_deg','reduction_rot_pct','observation'
    ]
    exists = os.path.isfile(csv_path)
    with open(csv_path, 'a', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=header)
        if not exists:
            w.writeheader()
        # Filter to header keys
        w.writerow({k: row_dict.get(k,'') for k in header})

@app.route('/stabilize-video', methods=['POST'])
def stabilize_video():
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

    ratio_thresh = float(request.args.get('ratio_thresh') or 0.75)

    if side_by_side and out is not None:
        out.release()
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

    # Always collect transforms for logging
    collect = True
    start_t = time.time()
    stats = stabilize_stream(cap, out, smooth_window=smooth_window, crop_ratio=crop_ratio,
                              collect_transforms=collect, overlay=overlay, side_by_side=side_by_side, scale=scale)
    elapsed = time.time() - start_t
    cap.release();
    if out is not None:
        out.release()

    # Compute run metrics if we have stats
    run_metrics = compute_summary_metrics(stats) if stats else {}
    duration_s = (run_metrics.get('frames',0) / fps) if fps else 0
    proc_fps = (run_metrics.get('frames',0) / elapsed) if elapsed > 0 else 0
    if run_metrics:
        run_metrics.update({
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'video': os.path.basename(input_path),
            'resolution': f"{width}x{height}",
            'duration_s': f"{duration_s:.2f}",
            'input_fps': f"{fps:.2f}",
            'proc_fps': f"{proc_fps:.2f}",
            'smooth_window': smooth_window,
            'crop': crop_ratio,
            'overlay': overlay,
            'side_by_side': side_by_side,
            'scale': scale,
        })
        run_metrics['observation'] = build_observation(run_metrics)
        try:
            os.makedirs('output', exist_ok=True)
            append_run_log(os.path.join('output','stabilization_runs.csv'), run_metrics)
        except Exception:
            pass

    if request.args.get('json') == '1':
        if stats is not None:
            try:
                os.makedirs('output', exist_ok=True)
                with open(os.path.join('output', f'{os.path.splitext(os.path.basename(output_path))[0]}_stats.json'), 'w', encoding='utf-8') as f:
                    json.dump(stats, f)
            except Exception:
                pass
        payload = {
            "video": os.path.basename(input_path),
            "output": os.path.basename(output_path),
            "frames": 0 if stats is None else len(stats),
            "smooth_window": smooth_window,
            "crop_ratio": crop_ratio,
            "overlay": overlay,
            "side_by_side": side_by_side,
            "scale": scale,
            "transforms": stats or []
        }
        if run_metrics:
            payload['metrics'] = run_metrics
        return jsonify(payload)

    if stats is not None:
        try:
            with open(os.path.join('output', f'{os.path.splitext(os.path.basename(output_path))[0]}_stats.json'), 'w', encoding='utf-8') as f:
                json.dump(stats, f)
        except Exception:
            pass

    resp = send_file(output_path, as_attachment=False, mimetype=mimetype)
    resp.headers['X-Input-Video'] = os.path.basename(input_path)
    resp.headers['X-Smooth-Window'] = str(smooth_window)
    resp.headers['X-Crop-Ratio'] = f"{crop_ratio:.4f}"
    resp.headers['X-Overlay'] = '1' if overlay else '0'
    resp.headers['X-SideBySide'] = '1' if side_by_side else '0'
    resp.headers['X-Output-Video'] = os.path.basename(output_path)
    resp.headers['X-Ratio-Thresh'] = f"{ratio_thresh:.2f}"
    if run_metrics:
        resp.headers['X-Avg-Features'] = f"{run_metrics['avg_features']:.1f}"
        resp.headers['X-Inlier-Ratio'] = f"{run_metrics['inlier_ratio_pct']:.1f}%"
        resp.headers['X-Fallback-Pct'] = f"{run_metrics['fallback_pct']:.1f}%"
        resp.headers['X-Jitter-Reductions'] = (
            f"dx:{run_metrics['raw_jitter_dx']:.2f}->{run_metrics['stab_jitter_dx']:.2f}({run_metrics['reduction_dx_pct']:.0f}%)|"
            f"dy:{run_metrics['raw_jitter_dy']:.2f}->{run_metrics['stab_jitter_dy']:.2f}({run_metrics['reduction_dy_pct']:.0f}%)|"
            f"rot:{run_metrics['raw_jitter_rot_deg']:.2f}->{run_metrics['stab_jitter_rot_deg']:.2f}({run_metrics['reduction_rot_pct']:.0f}%)" )
    if stats is not None:
        resp.headers['X-Frames'] = str(len(stats))
    return resp


@app.get('/stats')
def get_stats():
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

@app.route('/process-video', methods=['POST'])
def legacy_endpoint():
    return jsonify({"error": "Deprecated. Use /stabilize-video endpoint.", "use": "/stabilize-video"}), 410

if __name__ == '__main__':
    os.makedirs('input', exist_ok=True)
    os.makedirs('output', exist_ok=True)
    app.run(port=5000, debug=True)



