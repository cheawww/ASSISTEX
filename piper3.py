import cv2
import RPi.GPIO as GPIO
from smbus import SMBus
from pytesseract import pytesseract
import numpy as np
import subprocess
import os
import time


# Initialize GPIO
GPIO.setmode(GPIO.BCM)
bReading = 27
bCapturing = 16
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Piper TTS configuration
PIPER_MODEL = "en_US-hfc_female-medium.onnx"
PIPER_BINARY = "./piper/piper"

# I2C Address for the device
addr = 0x8
bus = SMBus(1)

def preprocess_image(image_path):
    """
    Preprocess the captured image to enhance OCR performance.
    """
    try:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError("Failed to load image. Check if the file exists and is readable.")

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (0, 0), sigmaX=70, sigmaY=70)
        divide = cv2.divide(gray, blur, scale=255)
        thresh = cv2.threshold(divide, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        kernal = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
        processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernal)

        # Debugging
        print("Preprocessing successful. Image shape:", processed.shape)

        return processed
    except Exception as e:
        print(f"Error during image preprocessing: {e}")
        return None

def capture_image():
    """
    Capture an image from the camera and save it as 'frame.png'.
    """
    print("Capturing image...")
    video_capture = cv2.VideoCapture(0)
   
    video_capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'YUYV'))
    video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
    video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 2160)
    if not video_capture.isOpened():
        print("Error: Unable to access the camera.")
        return False

    ret, frame = video_capture.read()
    video_capture.release()

    if not ret:
        print("Error: Failed to capture image.")
        return False

    cv2.imwrite("frame.png", frame)
    print("Image saved as 'frame.png'.")
    return True



def read_text_from_image(image_path="frame.png"):
    """
    Read text from an image using OCR.
    """
    print("Reading text from image...")

    if not os.path.exists(image_path):
        print("Error: No image file found.")
        os.system("cvlc --play-and-exit --quiet no_image.wav")
        return

    processed_image = preprocess_image(image_path)

    if processed_image is None:
        print("Error: Image preprocessing failed.")
        os.system("cvlc --play-and-exit --quiet process_error.wav")
        return

    text = pytesseract.image_to_string(processed_image, lang="eng")

    if text.strip():
        print(f"Detected text: {text}")
        command = f'echo "{text}" | {PIPER_BINARY} --model {PIPER_MODEL} --output_file audio.wav'
        subprocess.run(command, shell=True, executable="/bin/bash", check=True)

        os.system("cvlc --play-and-exit --quiet audio.wav")
    else:
        print("No text detected in the image.")
        os.system("cvlc --play-and-exit --quiet no_text.wav")

def volume_control():
    """
    Adjust system volume based on input from the I2C device.
    """
    try:
        while True:
            data = bus.read_byte(addr)
            volume_percentage = str(data)
            cmd = f"amixer -q sset Master {volume_percentage}%"
            os.system(cmd)
            time.sleep(0.1)
    except Exception as e:
        print(f"Volume control error: {e}")

def main_loop():
    """
    Main loop to handle button presses for capturing and reading.
    """
    while True:
        try:
            bReadingState = GPIO.input(bReading)
            bCapturingState = GPIO.input(bCapturing)
            if bCapturingState == 1: #ปุ่มกลม
                print("Capture button pressed.")
                os.system("cvlc --play-and-exit --quiet capture_start.wav")
                #tts.tts_to_file(text="Capturing image now.", file_path="capture_start.wav")
                if capture_image():
                    print("Image captured successfully.")
                read_text_from_image()
                time.sleep(0.1)
               
            if bReadingState == 1: #ปุ่มเหลี่ยม
                print("Read button pressed.")
                os.system("cvlc --play-and-exit --quiet read_start.wav")
                read_text_from_image()
                time.sleep(0.1)
       
        except cv2.error: #if it have error
            continue

if __name__ == "__main__":
    print("Welcome to ASSISTEX a Text and speak system...")
    os.system("cvlc --play-and-exit --quiet welcome.wav")
    #tts.tts_to_file(text="Welcome to the OCR and Text to Speech system.", file_path="welcome.wav")

    # Start volume control in the background
    from multiprocessing import Process
    volume_process = Process(target=volume_control)
    volume_process.start()

    # Run the main loop
    main_loop()

    # Clean up on exit
    volume_process.terminate()
    GPIO.cleanup()

