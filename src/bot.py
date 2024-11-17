from enum import Enum
import time
import threading
from screen_capture import ScreenCapture
from strategy import Game
import yolo_detection
import pyautogui

USER_BET_AMOUNT = 0
USER_BALANCE = 0

class GamePhase(Enum):
    BETTING = 1
    DRAWING = 2
    DECISION = 3
    PLAYING = 4

class Bot:
    def __init__(self):
        self.frame_count = 0
        self.player_val = 0
        self.player_hand = 0
        self.prev_player_val = None
        self.player_cards = []
        self.screen_cap = ScreenCapture()
        self.m_game = None
        self.bet_amount = 0
        
        # should make this persist
        self.player_balance = 0

        self.phase = None
    
        self.decision = None

        self.player_soft = False


        # phase flags
        self.game_in_progress = False # if wait for next game -> set true.
        self.bet_placed = False
        self.cards_dealt = False 
        self.decision_made = False

        self.yolo_model = None
        self.running = False


    def initialize_yolo(self):
        self.yolo_model = yolo_detection.DetectionModel('data/weights/best.pt')
        print("Yolo initialized")


    def start_game(self, player_cards, dealer_upcard):
        if len(player_cards) == 2 and dealer_upcard != "":
            self.cards_dealt = True

            if self.blackjack(sum(map(int, player_cards))):
                self.end_game()
                time.sleep(3)
                return
    
            game = Game(player_cards, dealer_upcard)
            game.set_soft_hand(self.player_soft)

            first_decision = game.make_decision()
            print("game started")
            return game, first_decision
        
        print("game not started, some cards missing")
        return None

    def process_game_frame(self, img):
        _, _, game_status = self.screen_cap.process_frame(img)
        print("game status:", game_status)
        ## WAITING FOR PLAYERS -> OTHER PLAYERS ARE DOING THINGS... (stand while others hit, or hit while others split etc.)
                # can read but no point?

        ## STATUS TRIGGERS

        # BETTING
             # PLEASE PLACE YOUR BETS - 5
             # LAST BETS - 4
             # BETS CLOSED

        # DRAWING
            # BETS ACCEPTED -> DEALING

        # DECISION
            # MAKE YOUR DECISION - number

        # PLAYING
            # WAITING FOR OTHER PLAYERS
            # TODO: bot will read current cards if "waiting for other players" used as trigger for playing phase
            # DEALING

        if "wait for next game" in game_status.lower():
            # if self.game_in_progress:
                # self.end_game()  # If the bot is in a game, end it
                # self.game_in_progress = False  # Set the flag to indicate no game is in progress
            print("Waiting for the next game to start...")
            return  # Skip further processing and wait for the next game


        # sometimes status bar dissapears
        if any(status in game_status.lower() for status in ["please place your bets", "last bets", "bets closed"]):
            self.phase = GamePhase.BETTING
        elif any(status in game_status.lower() for status in ["bets accepted", "dealing"]) and not self.cards_dealt:
            self.phase = GamePhase.DRAWING
        elif "make your decision" in game_status.lower():
            self.phase = GamePhase.DECISION
        elif any(status in game_status.lower() for status in ["waiting for other players", "dealing"]) and self.cards_dealt:
            self.phase = GamePhase.PLAYING
        else:
            print("no status detected")


        if self.phase == GamePhase.BETTING and not self.bet_placed:
            print("current phase:", self.phase)
            self.process_betting_phase(img)
        elif self.phase == GamePhase.DRAWING and not self.cards_dealt:
            print("current phase:", self.phase)
            self.process_drawing_phase(img)
        elif self.phase == GamePhase.DECISION and not self.decision_made:
            print("current phase:", self.phase)
            self.process_decision_phase(img)
        elif self.phase == GamePhase.PLAYING:
            print("current phase:", self.phase)

            self.decision_made = False

            if self.decision == "hit":
                self.process_playing_phase_hit(img)
            elif self.decision == "stand":
                self.process_playing_phase_stand(img)
            elif self.decision == "double":
                # TODO: add logic for double
                pass
            elif self.decision == "split":
                # TODO: add logic for split
                pass    

    def process_betting_phase(self, img):
        # resize image to 640x640 (if necessary)
        detect_results = self.yolo_model.detect(img)

        if detect_results["bet_one"] and detect_results["bet_five"] and detect_results["bet_ten"] and detect_results["bet_button"]:
            bet_one_x, bet_one_y = detect_results["bet_one_location"]
            bet_five_x, bet_five_y = detect_results["bet_five_location"]
            bet_ten_x, bet_ten_y = detect_results["bet_ten_location"]
            bet_button_x, bet_button_y = detect_results["bet_button_location"]

            bet_amount = USER_BET_AMOUNT
            if bet_amount > self.player_balance:
                print("Insufficient balance.")
                return
            
            while bet_amount >= 10:
                pyautogui.click(bet_ten_x, bet_ten_y)
                bet_amount -= 10
            while bet_amount >= 5:
                pyautogui.click(bet_five_x, bet_five_y)
                bet_amount -= 5
            while bet_amount >= 1:
                pyautogui.click(bet_one_x, bet_one_y)
                bet_amount -= 1

            pyautogui.click(bet_button_x, bet_button_y)
            self.bet_placed = True
            self.player_balance -= USER_BET_AMOUNT

            # print("Bet placed:", self.bet_amount)

    def parse_player_ace(self, player_value):
        if "/" in player_value:
            low_value, high_value = player_value.split("/")
            if high_value == "11":
                self.player_soft = True

            return low_value, high_value
        

    def parse_dealer_ace(self, dealer_value):
        if "/" in dealer_value:
            low_value, high_value = dealer_value.split("/")

            # if high_value == "11":
            #     self.dealer_ace = True

            return low_value, high_value

    
    def process_drawing_phase(self, img):
        player_value, dealer_value = self.screen_cap.process_frame(img)

        parsed_dealer_val = self.parse_dealer_ace(dealer_value)
        _, player_value = self.parse_player_ace(player_value)

        # TODO: ace value logic may not be correct... want to keep value as x/xx, but want to store the actual value in list

        if not self.cards_dealt:
            # if player_value is not empty and prev_player_val is empty, then it's the first card
            if self.prev_player_val == "" and player_value != "":  
                self.prev_player_val = player_value
                print("First card detected and added to hand:", player_value)
                self.player_cards.append(player_value)

            # if player_value is not empty and prev_player_val is not empty, then it's a new card need to subtract ot get actual card value.
            elif player_value != "":
                if self.prev_player_val != "" and self.prev_player_val !=  player_value:
                    if self.blackjack(player_value):
                        return

                    card_val = int(player_value) - int(self.prev_player_val)
                    self.player_cards.append(card_val)
                    print("New card added:", card_val)
                    self.prev_player_val = player_value

                result = self.start_game(self.player_cards, parsed_dealer_val)
                if result is not None:
                    self.m_game, self.decision = result
                    return
            else:
            # Update prev_player_val to current player value if it's valid
                self.prev_player_val = player_value

    def process_playing_phase_hit(self, img):
        player_value, _ = self.screen_cap.process_frame(img)

        # HIT [A, 4] soft -> [A, 4, A] soft
        # frame 1 : player_value = 5/15 [A, 4]
        # frame 2 : prev_low = 5
        #           prev_high = 15
        #           player_value = 6/16 (ace added) [A, 4, A]


        
        # checks if player_value is not empty and prev_player_val is not empty and not equal to player_value
        if self.prev_player_val != "" and self.prev_player_val !=  player_value:
            if self.blackjack(player_value):
                self.end_game()
                # what does this return do?
                return
            
            if ("/" in player_value and "/" in self.prev_player_val):
                # soft hand case 
                _, high_val = self.parse_player_ace(player_value)
                _, prev_high = self.parse_player_ace(self.prev_player_val)

                new_card_val = int(high_val) - int(prev_high)

                if self.update_player_hand(new_card_val, True):
                    return
                
                self.prev_player_val = player_value

            elif ("/" not in player_value and "/" in self.prev_player_val):
                # soft hand -> hard hand
                prev_low, _ = self.parse_player_ace(self.prev_player_val)
                new_card_val = int(player_value) - int(prev_low)
                if self.update_player_hand(new_card_val, False):
                    return # BUST case

                self.prev_player_val = player_value

            elif ("/" not in player_value and "/" not in self.prev_player_val):
                # hard hand case 
                new_card_val = int(player_value) - int(self.prev_player_val)
                if self.update_player_hand(new_card_val, False):
                    return

                self.prev_player_val = player_value 
        
    
    def process_playing_phase_stand(self, img):
        _, dealer_value = self.screen_cap.process_frame(img)

        if self.blackjack(dealer_value):
            self.end_game()
            return

        # dealer stands
        if dealer_value >= 17 and dealer_value <= 21:
            self.end_game()
            return
        
        # dealer busts
        if dealer_value > 21:
            self.end_game()
            return
        
        
    def process_playing_phase_double(self, img):
        pass

    def process_playing_phase_split(self, img):
        pass

    def process_decision_phase(self, img):
        # resize image to 640x640 (if necessary)
        detect_results = self.yolo_model.detect(img)

        if (detect_results["hit"] and detect_results["stand"] and detect_results["double"] and detect_results["split"]):
            hit_x, hit_y = detect_results["hit_location"]
            stand_x, stand_y = detect_results["stand_location"]
            double_x, double_y = detect_results["double_location"]
            split_x, split_y = detect_results["split_location"]

            if self.decision == "hit":
                pyautogui.click(hit_x, hit_y)
            elif self.decision == "stand":
                pyautogui.click(stand_x, stand_y)
            elif self.decision == "double":
                pyautogui.click(double_x, double_y)
            elif self.decision == "split":
                pyautogui.click(split_x, split_y)

            self.decision_made = True

    def update_player_hand(self, new_card_val, is_soft):
        self.player_cards.append(new_card_val)
        print("new card added, player hand is now:", self.player_cards)
        self.decision = self.m_game.new_card(new_card_val)
        self.m_game.set_soft_hand(is_soft)

        if (self.decision == "bust"):
            print("Bust! Game over.")
            self.end_game()
            return

        print("decision updated to:", self.decision)
        return False

    def blackjack(self, value):
        if value == "21":
            print("Blackjack... Game over.")
            # TODO: add logic to count dealer card as well in case of tie.
            return True

    def update_balance(self, outcome):
        if outcome == "win":
            self.player_balance += USER_BET_AMOUNT * 2
        elif outcome == "push":
            self.player_balance += USER_BET_AMOUNT
        print(f"Game outcome: {outcome}. Updated balance: {self.player_balance}")


    def end_game(self):
        print("Game ended, waiting for next game.")
        self.cards_dealt = False
        self.player_val = 0
        self.prev_player_val = 0
        self.player_cards = []
        self.m_game = None
        self.bet_amount = 0
        self.bet_placed = False
        self.decision = None
        self.decision_made = False
        self.game_in_progress = False
        self.player_soft = False

    def run(self):
        print("Welcome to bj bot :P")
        print("Please make sure the game is running and visible on your screen.")
        print("Type quit at any time to stop the bot")
        print("Please enter your balance and bet amount to begin.")

        # while True:
        #     user_input = input("type in quit to exit: ").strip()

        #     if user_input.lower() == "quit":
        #         print("Bot will stop ...")
        #         self.running = False
        #         break
        #     else:
        #         print("Invalid input. Please type 'quit' to exit.")

        while True:
            try:
                self.player_balance = int(input("Enter your balance: ").strip())
                USER_BET_AMOUNT = int(input("Enter your bet amount: ").strip())
                if USER_BET_AMOUNT > self.player_balance:
                    print("Bet amount cannot exceed balance. Please enter a valid bet amount.")
                else:
                    break
            except ValueError:
                print("Invalid input. Please enter a valid number.")

        print(f"\nBalance set to: {self.player_balance}")
        print(f"Bet amount set to: {USER_BET_AMOUNT}\n")
        print("Bot is now running")
        self.running = True
        self.initialize_yolo()


        # GPT terminal input and bet amount setting
        # input_thread = threading.Thread(target=self.set_bet_amount, daemon=True)
        # input_thread.start()

        while self.running: 
            if self.frame_count % 2 == 0:
                img = self.screen_cap.capture_screen()
                self.process_game_frame(img)

            self.frame_count += 1
            time.sleep(0.05)
        
        # input_thread.join()
        # print("Bot stopped")

if __name__ == "__main__":
    processor = Bot()
    processor.run()