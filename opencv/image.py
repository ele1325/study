import cv2
import pytesseract
import numpy as np
import time
import threading

def open_camera():
    cam = cv2.VideoCapture(1)  # Open the camera
    if not cam.isOpened():
        raise RuntimeError("Cannot open the camera")
    # 固定曝光和增益（如果支持）
    cam.set(cv2.CAP_PROP_EXPOSURE, -8)  # 曝光值（視攝影機而定，通常負數表示手動模式）
    cam.set(cv2.CAP_PROP_GAIN, 0)       # 增益值

    return cam

def show_camera(cam):

    while True:
        ret, frame = cam.read()  # Read a frame
        if not ret:
            print("Failed to grab frame")
            break

        cv2.imshow('Camera', frame)  # Display the frame
        cv2.moveWindow('Camera', 100, 100)  # Move the window

        if cv2.waitKey(1) != -1:  # Press any key to exit
            break

    cam.release()  # Release the camera
    # cv2.destroyAllWindows()  # Close the display window

def release_camera(cam):
    cam.release()  # Release the camera

def take_photo(cam, image_path):
    if not cam.isOpened():
        raise RuntimeError("Camera is not opened")
    time.sleep(1)  # Wait for the camera to warm up    
    ret, frame = cam.read() # Read a frame
    if not ret:
        raise RuntimeError("Cannot read the frame")
    # Save the image
    cv2.imwrite(image_path, frame)

def preprocess_image(image):

    # 灰階處理
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # 二值化處理
    _, image = cv2.threshold(image, 100, 255, cv2.THRESH_BINARY_INV)
    # 膨胀操作（增强文字区域）
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    image = cv2.dilate(image, kernel, iterations=1)
    # 邊緣檢測
    edges = cv2.Canny(image, 50, 150)
    # 輪廓檢測
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # 找到最大輪廓（假設最大輪廓是文字區域）
    largest_contour = max(contours, key=cv2.contourArea)
    # 計算最小外接矩形
    rect = cv2.minAreaRect(largest_contour)
    box = cv2.boxPoints(rect)
    box = np.int8(box)
    # 計算旋轉角度
    angle = rect[-1]
    if angle < -45:
        angle = angle + 90
    # 旋轉影像校正
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, rotation_matrix, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    return rotated

def is_bmw_text(image_path):
    """Use OCR to determine if the photo contains the text 'BMW'"""
    img = cv2.imread(image_path)
    cv2.imshow('Image', img)
    cv2.moveWindow('Image', 800, 100)
    cv2.imwrite(image_path, img)
    cv2.waitKey(800)  # Wait for a key event

    img = preprocess_image(img)
        # Display the preprocessed image
    cv2.imshow('Image', img)
    cv2.imwrite('./photo/bmw_result.jpg', img)
    cv2.waitKey(800)  # Wait for a key event

    # Use OCR
    text = pytesseract.image_to_string(img, config='--psm 7')
    print(text)
    return "BMW" in text

def is_center_color(image_path, color):
    """Determine if the center region of the photo is the specified color"""
    img = cv2.imread(image_path)
    (h, w) = img.shape[:2]
    center_region = img[h//4:h*3//4, w//4:w*3//4]

    # Define color ranges
    color_ranges = {
        'red': [
            ([0, 50, 50], [10, 255, 255]),  # First red range
            ([170, 50, 50], [180, 255, 255])  # Second red range
        ],
        'green': ([35, 50, 50], [85, 255, 255]),
        'blue': ([90, 50, 50], [140, 255, 255]),
        'white': ([0, 0, 200], [180, 30, 255]),
        'black': ([0, 0, 0], [180, 255, 50])
    }

    if color not in color_ranges:
        raise ValueError("Unsupported color")

    # Convert to HSV color space
    hsv = cv2.cvtColor(center_region, cv2.COLOR_BGR2HSV)

    # Handle red specifically with two ranges
    if color == 'red':
        lower_color1, upper_color1 = map(np.array, color_ranges['red'][0])
        lower_color2, upper_color2 = map(np.array, color_ranges['red'][1])

        # Create two masks for the red ranges
        mask1 = cv2.inRange(hsv, lower_color1, upper_color1)
        mask2 = cv2.inRange(hsv, lower_color2, upper_color2)

        # Combine the masks
        mask = mask1 | mask2
    else:
        lower_color, upper_color = map(np.array, color_ranges[color])
        mask = cv2.inRange(hsv, lower_color, upper_color)

    # Calculate the ratio of the specified color pixels
    color_ratio = cv2.countNonZero(mask) / (center_region.size / 3)
    print(color_ratio)
    # Display the center region
    cv2.imshow('Image', center_region)
    cv2.moveWindow('Image', 800, 100)
    cv2.waitKey(800)
    # cv2.destroyAllWindows()

    return color_ratio > 0.5  # If the ratio of the specified color pixels is more than 50%, consider it as that color

if __name__ == "__main__":
    cam = open_camera()

    camera_thread = threading.Thread(target=show_camera, args=(cam,))
    camera_thread.start()
    photo_path = "./photo/photo.jpg"
    take_photo(cam, photo_path)
    if is_bmw_text(photo_path):
        print("The photo contains the text 'BMW'")
    else:
        print("The photo does not contain the text 'BMW'")

    color = 'red'  # Can be changed to 'red', 'green', 'white', 'black'
    if is_center_color(photo_path, color):
        print(f"The center region of the photo is {color}")
    else:
        print(f"The center region of the photo is not {color}")
