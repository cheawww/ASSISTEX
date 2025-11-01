import cv2
import RPi.GPIO as GPIO
from smbus import SMBus
from pytesseract import pytesseract
import os, sys, time, subprocess, multiprocessing

addr = 0x8
bus = SMBus(1)
GPIO.setmode(GPIO.BCM)
bReading = 27
bCapturing = 16

GPIO.setup(bReading, GPIO.IN)
GPIO.setup(bCapturing, GPIO.IN)
def CaptureImg():
    os.system('cvlc --play-and-exit --quiet /home/overwrld/project/final/a.w.wav') #os system library python
    counter = 0
    vid = cv2.VideoCapture(0)
    vid.set(3, 1920)
    vid.set(4, 1080)
    while counter <= 100:
        ret, frame = vid.read()
        counter += 1
    os.system("espeak -a 200 'Framing completed' -vaf+f5")
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (0,0), sigmaX = 70, sigmaY = 70)
    divide = cv2.divide(gray, blur, scale = 255)
    thresh = cv2.threshold(divide, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
    kernal = cv2.getStructuringElement(cv2.MORPH_RECT, (1,1))
    morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernal)
    if ret:
        cv2.imwrite("frame.png", morph)
        os.system("espeak -a 200 'Captured' -vaf+f5")
    else:
        os.system("espeak -a 200 'Error' -vaf+f5")
    vid.release()
    cv2.destroyAllWindows()
    os.system('cvlc --play-and-exit --quiet /home/overwrld/project/final/cap.w.wav')
    src = cv2.imread('frame.png')
    text = pytesseract.image_to_string(src, lang = 'eng')
    print(text)
    engine.say(text)
    engine.runAndWait()

def ReadAgain():
    os.system('cvlc --play-and-exit --quiet /home/overwrld/project/final/read.w.wav')
    engine = pyttsx3.init()
    engine.setProperty('rate', 125)   #ความเร็วในการพูด
    src = cv2.imread('frame.png')     #ดึงภาพ
    text = pytesseract.image_to_string(src, lang = 'eng') #ดึงข้อความจากภาพ
    engine.say(text) #พูดจากข้อความ
    engine.runAndWait() #จำเป็นต้องใส่

def VolumnControl():
    while True:
        data = bus.read_byte(addr)
        val = str(data)
        cmd = "anixer -q sset Master" + " " + val +"%"
        os.system(cmd)
def MainStatement(): #เช็คปุ่ม
    while True:
        try:
            bReadingState = GPIO.input(bReading)
            bCapturingState = GPIO.input(bCapturing)
            if bCapturingState == 1: #ปุ่มกลม 
                os.system("espeak -a 200 'Entering CaptureImg' -vaf+f5")
                CaptureImg()
                time.sleep(0.5)
            if bReadingState == 1: #ปุ่มเหลี่ยม
                os.system("espeak -a 200 'Entering ReadAgain' -vaf+f5")
                ReadAgain()
                time.sleep(0.5)

        except cv2.error: #if it have error
            os.system("espeak -a 200 'Cant detect any camera, please try again' -vaf+f5")
            os.system('cvlc --play-and-exit --quiet /home/overwrld/project/final/error_sound.mp3')
            continue

os.system("espeak -a 200 'welcome' -vaf+f5")
os.system('cvlc --play-and-exit --quiet /home/overwrld/project/final/welcome.mp3')
if name == 'main': # multiprocessing python
    script0 = multiprocessing.Process(target = VolumnControl)
    script1 = multiprocessing.Process(target = MainStatement)

    script0.start()
    script1.start()
