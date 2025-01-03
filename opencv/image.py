import cv2
import pytesseract
import numpy as np
import time

def take_photo(image_path):
    cap = cv2.VideoCapture(1)  # Open the camera
    if not cap.isOpened():
        raise RuntimeError("Cannot open the camera")
    
    time.sleep(1)  # Wait for the camera to warm up    
    ret, frame = cap.read() # Read a frame
    if not ret:
        raise RuntimeError("Cannot read the frame")

    # Save the image
    cv2.imwrite(image_path, frame)
    cap.release()  # Release the camera

def deskew_image(image):
    """Correct the skew of the text in the image"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    coords = np.column_stack(np.where(gray > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated

def is_bmw_text(image_path):
    """Use OCR to determine if the photo contains the text 'BMW'"""
    img = cv2.imread(image_path)

    # Correct the skew of the image
    img = deskew_image(img)

    # Preprocess the image
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    inverted_binary = cv2.bitwise_not(binary)

    # Display the preprocessed image
    cv2.imshow('Binary Image', inverted_binary)
    cv2.imwrite(image_path, inverted_binary)
    cv2.waitKey(0)  # Wait for a key event
    cv2.destroyAllWindows()  # Close the display window

    # Use OCR
    text = pytesseract.image_to_string(inverted_binary, lang='eng')
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
    cv2.imshow('Center Region', center_region)
    cv2.waitKey(1000)
    cv2.destroyAllWindows()

    return color_ratio > 0.5  # If the ratio of the specified color pixels is more than 50%, consider it as that color

if __name__ == "__main__":
    photo_path = "photo.jpg"
    take_photo(photo_path)
    # if is_bmw_text(photo_path):
    #     print("The photo contains the text 'BMW'")
    # else:
    #     print("The photo does not contain the text 'BMW'")

    color = 'red'  # Can be changed to 'red', 'green', 'white', 'black'
    if is_center_color(photo_path, color):
        print(f"The center region of the photo is {color}")
    else:
        print(f"The center region of the photo is not {color}")
