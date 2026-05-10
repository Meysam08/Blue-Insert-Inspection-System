import cv2
import numpy as np
import time
import os
import csv

# ----------------------------------------
# CONFIG
# ----------------------------------------
SAVE_OUTPUT = True  # Save inspection snapshots
SAVE_DIR = "inspection_snapshots"
os.makedirs(SAVE_DIR, exist_ok=True)

LOG_FILE = "inspection_log.csv"
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Blue_Detected", "Body_Detected", "Top_Ring_Detected", "Status", "Saved_Image"])

# ----------------------------------------
# CAMERA SETUP
# ----------------------------------------
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
    raise RuntimeError("Could not open webcam")

# ----------------------------------------
# REAL-TIME LOOP
# ----------------------------------------
while True:
    ret, img = cap.read()
    if not ret:
        print("[ERROR] Failed to capture frame")
        break

    output = img.copy()
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # -------------------------------
    # STEP 1: BLUE INSERT
    # -------------------------------
    lower_blue = np.array([90, 200, 170])
    upper_blue = np.array([140, 255, 255])

    blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
    kernel = np.ones((5, 5), np.uint8)
    blue_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_OPEN, kernel)
    blue_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    blue_center = None
    blue_radius = None
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 500:
            continue
        peri = cv2.arcLength(cnt, True)
        circularity = 4 * np.pi * area / (peri * peri + 1e-5)
        if circularity > 0.7:
            (cx, cy), r = cv2.minEnclosingCircle(cnt)
            blue_center = (int(cx), int(cy))
            blue_radius = int(r)
            cv2.circle(output, blue_center, blue_radius, (0, 255, 0), 2)
            cv2.putText(output, "Blue insert", (blue_center[0] - 40, blue_center[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            break

    # -------------------------------
    # STEP 2: WHITE BODY
    # -------------------------------
    body_detected = False
    if blue_center is not None:
        roi_margin_x = int(4.0 * blue_radius)
        roi_margin_y = int(5.0 * blue_radius)
        x1 = max(0, blue_center[0] - roi_margin_x)
        y1 = max(0, blue_center[1] - roi_margin_y)
        x2 = min(img.shape[1], blue_center[0] + roi_margin_x)
        y2 = min(img.shape[0], blue_center[1] + roi_margin_y)
        roi = img[y1:y2, x1:x2]
        roi_hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        lower_white = np.array([0, 10, 167])
        upper_white = np.array([180, 140, 255])
        white_mask = cv2.inRange(roi_hsv, lower_white, upper_white)
        kernel = np.ones((7, 7), np.uint8)
        white_mask = cv2.morphologyEx(white_mask, cv2.MORPH_CLOSE, kernel)
        white_mask = cv2.morphologyEx(white_mask, cv2.MORPH_OPEN, kernel)

        contours, _ = cv2.findContours(white_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        body_cnt = None
        max_area = 0
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > max_area:
                max_area = area
                body_cnt = cnt
        if body_cnt is not None and max_area > 3000:
            body_cnt = body_cnt + np.array([[x1, y1]])
            cv2.drawContours(output, [body_cnt], -1, (0, 255, 255), 2)
            body_detected = True
            cv2.putText(output, "Body detected", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

    # -------------------------------
    # STEP 3: TOP RING
    # -------------------------------
    top_ring_detected = False
    if blue_center is not None:
        roi_top_y1 = max(0, blue_center[1] - 5 * blue_radius)
        roi_top_y2 = blue_center[1] - int(0.5 * blue_radius)
        roi_top_x1 = max(0, blue_center[0] - 3 * blue_radius)
        roi_top_x2 = min(img.shape[1], blue_center[0] + 3 * blue_radius)

        roi_top = img[roi_top_y1:roi_top_y2, roi_top_x1:roi_top_x2]
        gray = cv2.cvtColor(roi_top, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=1.2, minDist=30,
                                   param1=50, param2=30, minRadius=15, maxRadius=70)
        if circles is not None:
            circles = np.uint16(np.around(circles))
            for c in circles[0, :1]:
                center = (c[0] + roi_top_x1, c[1] + roi_top_y1)
                radius = c[2]
                cv2.circle(output, center, radius, (255, 0, 0), 2)
                cv2.putText(output, "Top Ring", (center[0] - 40, center[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                top_ring_detected = True

    # -------------------------------
    # STEP 4: PASS / FAIL
    # -------------------------------
    status = "PASS" if blue_center and body_detected and top_ring_detected else "FAIL"
    color = (0, 255, 0) if status == "PASS" else (0, 0, 255)
    cv2.putText(output, f"STATUS: {status}", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    # -------------------------------
    # STEP 5: LOG RESULTS
    # -------------------------------
    timestamp = int(time.time())
    saved_image = ""
    if SAVE_OUTPUT and status == "PASS":
        saved_image = os.path.join(SAVE_DIR, f"inspection_{timestamp}.jpg")
        cv2.imwrite(saved_image, output)

    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, bool(blue_center), body_detected, top_ring_detected, status, saved_image])

    # -------------------------------
    # DISPLAY
    # -------------------------------
    cv2.imshow("Inspection Result", output)
    key = cv2.waitKey(1)
    if key == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()
