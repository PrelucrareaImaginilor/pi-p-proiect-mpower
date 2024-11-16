import numpy as np
import cv2 as cv

cap = cv.VideoCapture('recording.mp4')

# Get the frames per second (fps) of the video
fps = cap.get(cv.CAP_PROP_FPS)
delay = int(300 / fps)  # Calculate delay in milliseconds
backSub = cv.createBackgroundSubtractorMOG2()
while cap.isOpened():
    ret, frame = cap.read()
    
    if not ret:
        print("Failed to grab frame")
        break
    fg_mask = backSub.apply(frame)
    contours, hierarchy = cv.findContours(fg_mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    # Create a copy of the frame for drawing contours
    frame_with_contours = frame.copy()
    frame_ct = cv.drawContours(frame_with_contours, contours, -1, (0, 255, 0), 2)

    retval, mask_thresh = cv.threshold(fg_mask, 180, 255, cv.THRESH_BINARY)
    kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (3, 3))
    mask_eroded = cv.morphologyEx(mask_thresh, cv.MORPH_OPEN, kernel)

    min_contour_area = 500  # Define your minimum area threshold
    large_contours = [cnt for cnt in contours if cv.contourArea(cnt) > min_contour_area]

    # Create a separate copy of the frame for drawing rectangles
    frame_out = frame.copy()
    for cnt in large_contours:
        x, y, w, h = cv.boundingRect(cnt)
        frame_out = cv.rectangle(frame_out, (x, y), (x+w, y+h), (0, 0, 200), 3)
 
    # Display the frame with contours and the frame with rectangles separately
    # cv.imshow('Contours', frame_ct)
    cv.imshow('Rectangles', frame_out)
    if cv.waitKey(delay) & 0xFF == ord('e'):
        break
    
cap.release()
cv.destroyAllWindows()