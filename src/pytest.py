import cv2
import pytesseract
import numpy as np
import pyautogui
import time

# Function to capture the screen
def capture_screen():
    screenshot = pyautogui.screenshot()
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)  # Convert to BGR for OpenCV
    return screenshot

# Main loop to process video frames
frame_count = 0
while True:
    img = capture_screen()
    
    # TODO: Dynamic change
    screen_height, screen_width, _ = img.shape

    # ROIs for player, dealer, and words (adjust these based on your screen)
    w_x1 = int(screen_width * 0.41)
    w_x2 = int(screen_width * 0.58)
    w_y1 = int(screen_height * 0.47)
    w_y2 = int(screen_height * 0.52)

    d_x1 = int(screen_width * 0.48)
    d_x2 = int(screen_width * 0.53)
    d_y1 = int(screen_height * 0.51)
    d_y2 = int(screen_height * 0.56)

    p_x1 = int(screen_width * 0.44)
    p_x2 = int(screen_width * 0.48)
    p_y1 = int(screen_height * 0.78)
    p_y2 = int(screen_height * 0.85)

    # Get ROIs
    player_roi = img[p_y1:p_y2, p_x1:p_x2]
    dealer_roi = img[d_y1:d_y2, d_x1:d_x2]
    words_roi = img[w_y1:w_y2, w_x1:w_x2]

    # Process every 5th frame
    if frame_count % 5 == 0:
        player_gray = cv2.cvtColor(player_roi, cv2.COLOR_BGR2GRAY)
        dealer_gray = cv2.cvtColor(dealer_roi, cv2.COLOR_BGR2GRAY)
        words_gray = cv2.cvtColor(words_roi, cv2.COLOR_BGR2GRAY)
        
        _, player_thresh = cv2.threshold(player_gray, 127, 255, cv2.THRESH_BINARY)
        _, dealer_thresh = cv2.threshold(dealer_gray, 127, 255, cv2.THRESH_BINARY)
        _, words_thresh = cv2.threshold(words_gray, 127, 255, cv2.THRESH_BINARY)

        # Perform OCR on the thresholded images
        player = pytesseract.image_to_string(player_thresh, config='--psm 7')
        dealer = pytesseract.image_to_string(dealer_thresh, config='r--psm 7')
        words = pytesseract.image_to_string(words_thresh, config='--psm 7')

        # Print the detected values
        print(f"Detected player value: {player.strip()}")
        print(f"Detected dealer value: {dealer.strip()}")
        print(f"Detected words: {words.strip()}")

    # Show the ROIs in separate windows for visualization (optional)
    cv2.imshow('player_roi', player_roi)
    cv2.imshow('dealer_roi', dealer_roi)
    cv2.imshow('words_roi', words_roi)

    # Break on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    frame_count += 1
    time.sleep(0.05)  # To slow down the capture, so it's not running at maximum speed

# Release resources
cv2.destroyAllWindows()