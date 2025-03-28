
# Raspberry Pico Inspection System

This project implements a lightweight visual inspection system using a Raspberry Pi and camera module. The system captures, processes, and classifies images to detect manufacturing defects in small electronic devices such as PCBs.

## 📌 Features

- 📷 Captures images directly from a camera.
- ✂️ Crops the image to a region of interest (customizable per environment).
- 🔍 Sharpens and resizes the image to enhance quality and prevent resolution loss during upload.
- 📡 Sends the processed image to an API server to receive object detection results.
- 🧠 Based on detection results, categorizes the image as:
  - `pass` (correctly assembled),
  - `broken` (defective case detected),
  - `invalid` (unclear result, requires re-inspection).
- 📁 Saves the results with bounding boxes and logs the detection outcome in a `.txt` file.
- ⚠️ Includes defect categories like `NOCHIP`, `NOUSB`, etc. for improved model training.

## 📂 Folder Structure

```
project_root/
├── picodetection.py        # Main detection script
├── output/                 # Folder to store processed images
├── whatisthis.txt          # Project logic overview
└── ...
```

## 🛠 Requirements

- Python 3.x
- OpenCV
- Requests
- (Optional) Raspberry Pi with camera module

Install dependencies using:

```bash
pip install -r requirements.txt
```

> Note: Make sure to adjust the crop settings in the code to match your specific camera and setup.

## 📃 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## ✍️ Author

조현석 (Hyunseok Cho)
