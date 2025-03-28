import sys
import time
import serial
import requests
import numpy as np
import os
from io import BytesIO
from pprint import pprint
from requests.auth import HTTPBasicAuth
import cv2
import random
import tkinter as tk
from PIL import Image, ImageTk
from datetime import datetime

# 시리얼 포트 설정
ser = serial.Serial("/dev/ttyACM0", 9600)

# API 정보
api_url = "https://suite-endpoint-api-apne2.superb-ai.com/endpoints/d977978f-57ca-4003-8e41-afa311353c5d/inference"
ACCESS_KEY = "NuFJPAxnmW75TXC6AZgwN8jG36I57mHg8XSMlQNV"
USERNAME = "kdt2025_1-30"

# 이미지 저장 폴더 설정
SAVE_DIR = "./image"
os.makedirs(SAVE_DIR, exist_ok=True)
image_counter = 0

# 확대 비율
scale_factor = 2


color_map = {
    "USB": (0, 255, 255),  # Yellow
    "RASPBERRY PICO": (0, 165, 255),  # Orange
    "CHIPSET": (255, 0, 0),  # Blue
    "OSCILLATOR": (0, 255, 0),  # Green
    "BOOTSEL": (255, 0, 255),  # Purple
    "HOLE": (255, 255, 0),  # Cyan
    "NOCHIPSET": (0, 0, 0),  # Black
    "NOUSB": (0, 0, 0),  # Black
    "NOBOOTSEL": (0, 0, 0),  # Black
    "NOOSCILLATOR": (0, 0, 0),  # Black
}


# 저장할 객체 조건
required_counts = {
    "USB": 1,
    "RASPBERRY PICO": 1,
    "CHIPSET": 1,
    "OSCILLATOR": 1,
    "BOOTSEL": 1,
    "HOLE": 4
}

# 카메라 이미지 캡처 함수
def get_img():
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("Camera Error")
        return None
    ret, img = cam.read()
    cam.release()
    if not ret:
        print("Failed to capture image")
        return None
    return img

# 이미지 샤프닝 함수
def sharpen_image(img):
    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]])
    return cv2.filter2D(img, -1, kernel)

# 이미지 크롭 함수
def crop_img(img, size_dict):
    x, y, w, h = size_dict["x"], size_dict["y"], size_dict["width"], size_dict["height"]
    return img[y:y+h, x:x+w]

# 이미지 확대 함수
def zoomup(img, scale_factor):
    height, width = img.shape[:2]
    return cv2.resize(img, (width * scale_factor, height * scale_factor), interpolation=cv2.INTER_CUBIC)


def save_to_file(status_text, object_count):
    # 상태에 따라 다른 파일에 객체 데이터를 기록
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filename = f"{status_text.lower()}.txt"
    with open(filename, "a") as file:
        file.write(f"Timestamp: {current_time}\n")
        file.write(f"Status: {status_text}\n")
        for obj_class, count in object_count.items():
            file.write(f"{obj_class}: {count}\n")
        file.write("\n" + "="*30 + "\n")


# 추론 요청 함수
def inference_request(img: np.array):
    global image_counter
    _, img_encoded = cv2.imencode(".jpg", img)
    img_bytes = BytesIO(img_encoded.tobytes())

    try:
        response = requests.post(
            url=api_url,
            data=img_bytes,
            auth=HTTPBasicAuth(USERNAME, ACCESS_KEY),
            headers={"Content-Type": "image/jpeg"},
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            objects = result.get("objects", [])
            
            object_count = {}

            for obj in objects:
                if obj['score'] > 0:
                    obj_class = obj['class']
                    box = obj['box']
                    startpoint, endpoint = (box[0], box[1]), (box[2], box[3])
                    color = color_map.get(obj_class, (255, 255, 255))  # Default: White

                    cv2.rectangle(img, startpoint, endpoint, color, 2)
                    label = f"{obj_class} ({obj['score']:.2f})"
                    cv2.putText(img, label, (box[0], box[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

                    object_count[obj_class] = object_count.get(obj_class, 0) + 1

            
                # 첫번째 검사: 불량 검사 (NOCHIPSET, NOUSB, NOBOOTSEL, NOOSCILLATOR가 감지되면 broken)
            broken_classes = {"NOCHIPSET", "NOUSB", "NOBOOTSEL", "NOOSCILLATOR"}
            if any(cls in object_count for cls in broken_classes):
                status_text = "broken(RIGHT)"
                text_color = (0, 0, 255)  # 빨간색
            else:
                # 두 번째 검사: 객체 개수 검사 (총 9개여야 pass, 아니면 invalid)
                total_objects = sum(object_count.values())
                if total_objects == 9:
                    status_text = "pass(LEFT)"
                    text_color = (0, 255, 0)  # 초록색
                else:
                    status_text = "invalid(STRAIGHT)"
                    text_color = (0, 255, 255)  # 노란색
            # 상태 텍스트를 이미지에 추가
            cv2.putText(img, status_text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, text_color, 3)

            # 상태에 맞는 텍스트 파일에 객체 정보 저장
            save_to_file(status_text, object_count)


            save_path = os.path.join(SAVE_DIR, f"{image_counter}.jpg")
            cv2.imwrite(save_path, img)
            return img, status_text == "pass(LEFT)"
        else:
            print(f"Failed to send image. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending request: {e}")
    
    return None, False

# Tkinter GUI 클래스
class ImageWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Object Detection GUI")

        self.label = tk.Label(root)
        self.label.pack()

    def update_image(self, img, is_valid):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)

        
        draw = Image.new("RGBA", img_pil.size, (255, 255, 255, 0))
        painter = Image.new("RGB", img_pil.size, (255, 255, 255))
        painter.paste(img_pil, (0, 0))

        img_cv = np.array(painter)

        img_pil = Image.fromarray(img_cv)
        img_tk = ImageTk.PhotoImage(img_pil)

        self.label.config(image=img_tk)
        self.label.image = img_tk

# 메인 루프
def main_loop(window):
    global image_counter

    while True:
        print("Waiting for data from serial port...")
        data = ser.read()
        print(f"Received data: {data}")

        if data == b"0":
            start_time = time.time()
            time.sleep(0.1)
            img = get_img()
            if img is None:
                continue

            crop_info = {"x": 210, "y": 100, "width": 350, "height": 350}
            img = crop_img(img, crop_info)
            img = sharpen_image(img)
            img = zoomup(img, scale_factor)

            image_counter += 1
            img_with_boxes, is_valid = inference_request(img)

            if img_with_boxes is not None:
                window.update_image(img_with_boxes, is_valid)
                print("Sending '1' to serial port")
                ser.write(b"1")

            print(f"Execution time: {time.time() - start_time:.2f} seconds")

# 프로그램 실행
if __name__ == "__main__":
    root = tk.Tk()
    window = ImageWindow(root)

    from threading import Thread
    thread = Thread(target=main_loop, args=(window,))
    thread.daemon = True
    thread.start()

    root.mainloop()