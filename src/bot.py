from enum import Enum
import time
import keyboard
from screen_capture import ScreenCapture
from strategy import Game
import sys
import select
import yolo_detection
import pyautogui

#TODO: implement yolo training to detect card
        # action returns inital decision
        # give to yolo to detect button + pythongui to hit button


# plan


#  bot is the main running will run the Game
#       it uses the ScreenCapture class 
#           to get video every frame, get rois and get what they read with ocr (pytesseract)
#           then return to the bot, along with the original frame

#       bot will send frame to yolo class, where frame will be processed and run on yolo (detect)
#           yolo will detect the betting area, the betting options, and the hit stand double (later split) buttons and send to bot
#           bot will then send the decision to the pythongui class to click the button

#           if yolo detects both betting option + bet button, send to bot,
#           else if it detects both hit and stand and other options, send to bot
#           if nothing is detected, do nothing?

 
#           if both betting options are detected, check bet_placed = True (bot class) + bet_amount = True (bot class)


#           check given to bot bet_placed = True + amount = True
#           
# 
#  
#
#               decision is made by the bot based off of what is detected etc.
#                  bot will then send the decision to the pythongui class to click the button 
#                   bot will have vars =  
#                       bet_placed = False
#                       bet_amount = 0
#                       decision = None
#                       cards_dealt = False
#                       player_val = 0
#                       prev_player_val = 0
#                       player_cards = []
#                       screen_cap = ScreenCapture()
#                       m_game = None


USER_BET_AMOUNT = 0

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
        self.prev_dv = 0
        self.player_cards = []
        self.screen_cap = ScreenCapture()
        self.m_game = None
        self.bet_amount = 0
        self.bet_placed = False
        self.decision = None
        self.player_ace = False
        self.game_in_progress = False # if wait for next game -> set true.
        self.cards_dealt = False # change to cards dealt
        self.decision_made = False
        self.dealer_ace = False

        self.yolo_model = yolo_detection.DetectionModel('data/weights/best.pt')


    def start_game(self, player_cards, dealer_upcard):
        if len(player_cards) == 2 and dealer_upcard != "":
            if sum(map(int, self.player_cards)) == 21:
                    print("Blackjack! Player wins.")
                    self.end_game()
                    #TODO stop loop and wait for next game
                    time.sleep(3)
                    return
            
            game = Game(player_cards, dealer_upcard)
            first_decision = game.make_decision()
            self.cards_dealt = True
            print("game started")
            return game, first_decision
        
        print("game not started, some cards missing")
        return None

    def is_there_game(self):
        pass

    def end_game(self):
        pass

    def process_game_frame(self, img):
        # read status player and dealer val in process_game_frame
        # pass dealer and player vals to process_game 


        # or process here seperately and do ocr twice one for status one for numbers.

        game_status = self.ocr_read_status(img)
        print("game status:", game_status)

        ## BETS PLACED / BETS CLOSED == start reading cards, small delay between BETS PLACED and DEALING.

        ## WAITING FOR PLAYERS -> OTHER PLAYERS ARE DOING THINGS... (stand while others hit, or hit while others split etc.)
                # can read but no point?

        #

        if "bets" in game_status.lower() and not "bets placed" in game_status.lower():
            self.phase = GamePhase.BETTING
        elif "dealing" or "bets placed" in game_status.lower() and self.cards_dealt == False:
            # INTIAL DRAWING PHASE, read cards while status says dealing, bets placed, and cards haven't all been dealt yet.
            self.phase = GamePhase.DRAWING
        elif "make your decision" or "dealing" in game_status.lower():
            self.phase = GamePhase.DECISION
        elif "waiting for other players" or "dealing" in game_status.lower():
            self.phase = GamePhase.PLAYING


        if self.phase == GamePhase.BETTING and self.bet_placed == False:
            self.process_betting_phase(img)
        elif self.phase == GamePhase.DRAWING and self.cards_dealt == False:
            self.process_drawing_phase(img)
        elif self.phase == GamePhase.DECISION and self.decision_made == False:
            # once decision is clicked status will show "wait for other players" then switch to "dealing" when all players are done
            # should check for both and continue reading depending on the decisoin that was made. stand -> only read dealer, hit -> read player.
            self.process_decision_phase(img)
        elif self.phase == GamePhase.PLAYING:
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
        # resize image to 640x640?
        detect_results = self.yolo_model.detect(img)

        if (detect_results["bet_one"] and detect_results["bet_five"] and detect_results["bet_ten"] and detect_results["bet_button"]):

            bet_button_x, bet_button_y = detect_results["bet_button_location"]
            pyautogui.click(bet_button_x, bet_button_y)
            self.bet_placed = True

            self.bet_amount = USER_BET_AMOUNT

    def process_drawing_phase(self, img):
        player_value, dealer_value = self.screen_cap.process_frame(img)

        # TODO: make sure cards aren't read incorrectly and add logic to counter that.
        # TODO: add logic to count dealer card in case of ace. Set dealer_ace to true and logic for Insurance

        if "/" in player_value:
            player_value = "11"

        print("player value:", player_value)
        print("dealer value:", dealer_value)

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

                result = self.start_game(self.player_cards, dealer_value)
                if result is not None:
                    self.m_game, self.decision = result
                    return
            else:
            # Update prev_player_val to current player value if it's valid
                self.prev_player_val = player_value

    def process_playing_phase_hit(self, img):
        # TODO: TEST THIS
        player_value, _ = self.screen_cap.process_frame(img)

        if self.prev_player_val != "" and self.prev_player_val !=  player_value:
            if self.blackjack(player_value):
                return

            new_card_val = int(player_value) - int(self.prev_player_val)
            self.player_cards.append(new_card_val)
            print("new card added, player hand is now:", self.player_cards) 
            self.decision = self.m_game.new_card(new_card_val)
            print("decision updated to:", self.decision)
            self.prev_player_val = player_value 

    def process_playing_phase_stand(self, img):
        #TODO: TEST THIS
        _, dealer_value = self.screen_cap.process_frame(img)
        if (dealer_value >= 17):
            #TODO: add logic to record win/loss/push
            self.end_game()
            return

    def process_decision_phase(self, img):
        # take img and give to yolo to detect hit stand double split
        # if hit stand double split detected, make decision (click button)
        # set decision_made = True

        # status will change to "waiting for other players" then "dealing" when all players are done but small delay between the two so start reading at "waiting for other players"

        self.decision_made = True

    def blackjack(self, player_value):
        if player_value == "21":
            print("Blackjack... Game over.")
            # TODO: add logic to count dealer card as well in case of tie.
            return True
    
    def check_dealer_card(self, dealer_value):

        if self.prev_dv != dealer_value:
            card_val = int(dealer_value) - int(self.prev_dv)
            self.m_game.dealer_hand.append(card_val)
            self.prev_dv = dealer_value

            # Check if dealer has stopped drawing cards
            if self.m_game.dealer_stands():
                self.end_game()
        pass


    def check_new_card(self, player_value):
        if (self.prev_player_val != player_value):
            card_val = int(player_value) - int(self.prev_player_val)
            self.player_cards.append(card_val)
            ## update new decision 
            self.decision = self.m_game.new_card(card_val)
            self.prev_player_val = player_value 


    def end_game(self):
        self.cards_dealt = False
        self.player_val = 0
        self.prev_player_val = 0
        self.player_cards = []
        self.m_game = None
        self.bet_amount = 0
        self.bet_placed = False
        self.decision = None


    def run(self):
        print("Bot is running")
        # TODO: add logic allowing user to stop, set bet amount,
        while True:
            # Capture screen every other frame
            if self.frame_count % 2 == 0:
                img = self.screen_cap.capture_screen()
                self.process_game_frame(img)
      
            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                input_line = sys.stdin.readline().strip()
                if input_line.lower() == "stop":
                    break

            self.frame_count += 1
            time.sleep(0.05)

if __name__ == "__main__":
    processor = Bot()
    processor.run()