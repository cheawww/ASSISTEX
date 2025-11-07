import cv2
import pytesseract

def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) # Convert to grayscale
    blur = cv2.GaussianBlur(gray, (5,5), 0) # Reduce noise
    binary = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1] # Binarization
    return binary

image = cv2.imread("handwritten_sample.jpg")
processed_image = preprocess_image(image)

cv2.imshow("Processed Image", processed_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
