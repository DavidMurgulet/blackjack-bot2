import unittest
from unittest.mock import MagicMock
from bot import Bot  # Import the Bot class from your script
import pyautogui  


class TestBotMethods(unittest.TestCase):
    def setUp(self):
        self.bot = Bot()
        self.bot.yolo_model = MagicMock()  # Mock YOLO model
        self.bot.screen_cap = MagicMock()  # Mock screen capture

    def test_process_betting_phase(self):
        # Simulate YOLO detection results
        self.bot.yolo_model.detect.return_value = {
            "bet_one": True,
            "bet_five": True,
            "bet_ten": True,
            "bet_button": True,
            "bet_one_location": (100, 200),
            "bet_five_location": (150, 200),
            "bet_ten_location": (200, 200),
            "bet_button_location": (250, 200),
        }

        # Mock pyautogui to prevent real clicks
        pyautogui.click = MagicMock()

        # Set USER_BET_AMOUNT for testing
        global USER_BET_AMOUNT
        USER_BET_AMOUNT = 16

        # Prepare a mock image
        mock_img = MagicMock()

        # Call the method
        self.bot.process_betting_phase(mock_img)

        # Check that clicks were performed correctly
        pyautogui.click.assert_any_call(200, 200)  # Bet 10
        pyautogui.click.assert_any_call(150, 200)  # Bet 5
        pyautogui.click.assert_any_call(100, 200)  # Bet 1
        pyautogui.click.assert_any_call(250, 200)  # Confirm bet

        # Ensure bet_placed is set to True
        self.assertTrue(self.bot.bet_placed)

    # Add similar tests for other methods...


if __name__ == "__main__":
    unittest.main()
