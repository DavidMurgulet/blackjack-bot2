import cv2
import numpy as np
import pyautogui
import easyocr


class ScreenCapture:
    def __init__(self, frame_skip=1):
        self.frame_count = 0
        self.player_cards = []
        # Initialize EasyOCR reader
        self.reader = easyocr.Reader(['en'], gpu=True)


    # def resize_image(img, scale_percent=50):
    #     width = int(img.shape[1] * scale_percent / 100)
    #     height = int(img.shape[0] * scale_percent / 100)
    #     return cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA)

    def load_image(self, image_path):
        # Load image from the file path
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not open or find the image: {image_path}")
        return img

    def capture_screen(self):
        self.frame_count += 1
        screenshot = pyautogui.screenshot()
        screenshot = np.array(screenshot)
        return cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

    
    def get_roi(self, img, x1, x2, y1, y2):
        return img[y1:y2, x1:x2]

    def extract_text_with_easyocr(self, roi):
        # Recognize text using EasyOCR (no need for thresholding or grayscale conversion)
        result = self.reader.readtext(roi, allowlist ='0123456789/', contrast_ths=0.5, adjust_contrast=0.7, decoder='greedy')
        # Extract and return the recognized text
        return ' '.join([text for _, text, _ in result])
    
    def test_single_frame(self, img):
        # Load the image
        img = self.load_image(img)
        
        # Process the frame and get the player and dealer values
        curr_player_value, dealer_value = self.process_frame(img)
        
        # Print out the OCR results
        print("Player Value:", curr_player_value)
        print("Dealer Value:", dealer_value)


    def process_frame(self, img):
        screen_height, screen_width, _ = img.shape

        # Define ROIs for player, dealer, and words
        rois = {
            "player": (int(screen_width * 0.445), int(screen_width * 0.469), int(screen_height * 0.81), int(screen_height * 0.833)),
            "dealer": (int(screen_width * 0.49), int(screen_width * 0.509), int(screen_height * 0.519), int(screen_height * 0.544))
            # "words": (int(screen_width * 0.41), int(screen_width * 0.58), int(screen_height * 0.47), int(screen_height * 0.52)),
        }

        # Extract ROIs
        player_roi = self.get_roi(img, *rois["player"])
        dealer_roi = self.get_roi(img, *rois["dealer"])
        # words_roi = self.get_roi(img, *rois["words"])

        # Perform OCR using EasyOCR on each ROI
        curr_player_value = self.extract_text_with_easyocr(player_roi)
        dealer_value = self.extract_text_with_easyocr(dealer_roi)
        # status_msg = self.extract_text_with_easyocr(words_roi)

        # Save the ROIs to the "rois" folder (optional for debugging)
        cv2.imwrite("rois/player_roi.png", player_roi)
        cv2.imwrite("rois/dealer_roi.png", dealer_roi)
        # cv2.imwrite("rois/words_roi.png", words_roi)

        return curr_player_value, dealer_value


if __name__ == "__main__":
    # Create an instance of ScreenCapture
    screen_capture = ScreenCapture()
    # Path to the image to test
    image_path = "dealer16_player18 .png"
    # Run the test function
    screen_capture.test_single_frame(image_path)