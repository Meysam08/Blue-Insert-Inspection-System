# Blue-Insert-Inspection-System

Computer vision system for real-time quality inspection of a product featuring a **blue insert**, a **white body**, and a **top ring**. The system uses a webcam, detects all three components, and logs pass/fail results with snapshots.

---

## 📁 Project Structure

```
.
├── HSVPickerTool.py        # Utility to pick HSV values from sample.jpg
├── fianl.py                # Main inspection script (real-time detection)
├── sample.jpg              # Reference image for HSV calibration
├── inspection_snapshots/   # Created automatically; stores PASS images
└── inspection_log.csv      # CSV log of all inspections
```

> **Note:** `fianl.py` is the main script (typo preserved from original).

---

## 🚀 Features

- **Real‑time detection** of:
  - Blue insert (circular, high saturation & value)
  - White body (large white region near insert)
  - Top ring (circular feature above insert, detected via Hough Circles)
- **Pass/Fail** logic: all three must be present.
- **Logging** – every frame is recorded in `inspection_log.csv` with timestamp and detection status.
- **Snapshot saving** – only PASS images are saved to `inspection_snapshots/`.
- **Visual feedback** – bounding boxes, labels, and status overlay on the live feed.

---

## 🧰 Requirements

Install the dependencies:

```bash
pip install opencv-python numpy
```

- Python 3.7+
- A working webcam (index 0 by default)

---

## 🎨 HSV Calibration (HSVPickerTool)

Before running the main script, you may need to adjust the HSV thresholds for your lighting conditions. Use `HSVPickerTool` to sample the blue insert from `sample.jpg`:

```bash
python HSVPickerTool.py
```

- Click on the blue area in the displayed image.
- The HSV values will be printed in the console.
- Update `lower_blue` and `upper_blue` in `fianl.py` accordingly.

**Current default blue range (fianl.py):**
```python
lower_blue = np.array([90, 200, 170])
upper_blue = np.array([140, 255, 255])
```

> 💡 You can also adjust the white body mask and Hough Circle parameters for the top ring.

---

## 🔧 Usage

Run the main inspection script:

```bash
python fianl.py
```

- The webcam feed will open.
- Press **ESC** to quit.
- Every inspection frame is evaluated; results are appended to `inspection_log.csv`.
- PASS images are saved automatically (if `SAVE_OUTPUT = True`).

### Configuration in `fianl.py`

| Variable         | Description                                    |
|------------------|------------------------------------------------|
| `SAVE_OUTPUT`    | Save snapshots of PASS inspections            |
| `SAVE_DIR`       | Folder for saved images                       |
| `LOG_FILE`       | CSV log file name                             |
| Camera settings  | Resolution 640×480, adjust `cap = cv2.VideoCapture(0)` if needed |

All detection parameters (morphology kernels, min area, circularity, Hough params) are clearly marked in the script and can be tuned for your product.

---

## 📊 Outputs

### Inspection Log (`inspection_log.csv`)

| Column               | Description                              |
|----------------------|------------------------------------------|
| Timestamp            | UNIX timestamp of the inspection         |
| Blue_Detected        | True/False                               |
| Body_Detected        | True/False                               |
| Top_Ring_Detected    | True/False                               |
| Status               | PASS if all three are True, else FAIL    |
| Saved_Image          | Path to saved snapshot (only for PASS)   |

### Snapshots

Only PASS images are stored in `inspection_snapshots/` with naming scheme:  
`inspection_<timestamp>.jpg`

---

## 🛠️ Customization Tips

- **Blue insert** – adjust `lower_blue`/`upper_blue` and `circularity` threshold.
- **White body** – modify `lower_white`/`upper_white` and `min_area` for the largest contour.
- **Top ring** – tune `param1`, `param2`, `minRadius`, `maxRadius` in `cv2.HoughCircles`.
- **ROI margins** – the search regions for body and ring are scaled by the blue insert radius. Adjust the multipliers (`4.0`, `5.0`, `3.0`, etc.) if the relative geometry differs.

---

## 🤝 Contributing

Feel free to open issues or pull requests to improve detection robustness, add new features, or fix typos (like the script name 😄).

---

## 📄 License

This project is open source and available under the MIT License.
