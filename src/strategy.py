#rules, chosen by player.
double_down_ace= False
split_on = False


player_cards = [] # list of cards
player_card_sum = 0
dealer_upcard = 0
bet_amount = 0
auto_bet = False

# YOLO training: 
#   hit stand double split
#   bet button
#   bet options
#   quit


# have player value and dealer upcard
    # TODO: have player values seperate
    
# main py == capture screen + preprocessing 
#     -> yolo detection === gives me hit stand etc PER frame
#     -> main.py give player value and dealer upcard PER frame
#             -> strategy.py does math and gives me hit stand logic etc PER frame
#                 -> main.py takes that logic and clicks with pythongui per frame


# NEEDS DETECTION FOR GAME END (blackjack, bust, win, lose)
class Game:
    def __init__(self, cards, dealer_upcard):
        self.player_hand = [cards]
        self.dealer_hand = [dealer_upcard]
        self.player_total = sum(self.player_hand)
        self.split_games = []  
        self.dealer_upcard = dealer_upcard
        self.double_possible = False
        self.split_possible = False

    def new_card(self, card):
        self.player_hand.append(card)
        self.player_total = sum(self.player_hand)        
        return self.make_decision()
    
    def new_dealer_card(self, card):
        self.dealer_hand.append(card)
        self.calculate_dealer_total()
        # check bust do someth

        if self.dealer_total > 21:
            return "dealer bust"
        
        #end game
        
        return


    def calculate_dealer_total(self):
        total = 0
        aces = 0

        # Calculate total while counting Aces separately
        for card in self.dealer_hand:
            if card == 11:  # Ace can be 11 or 1
                aces += 1
            total += card

        # Adjust total if Aces are present
        while total > 21 and aces:
            total -= 10  # Count an Ace as 1 instead of 11
            aces -= 1

        self.dealer_total = total

    def dealer_stands(self):
        while self.dealer_total < 17:
            self.new_dealer_card()
        return self.dealer_total
    


    def make_decision(self):
        has_ace = 1 in self.player_hand

        # Adjust the dealer upcard for Ace case (treat dealer ace as 11)
        dealer_upcard = self.dealer_upcard
        if dealer_upcard == 1:
            dealer_upcard = 11

        # Check if it's a soft hand (has ace counted as 11)
        if has_ace and self.player_total <= 11:
            # Soft totals logic
            if self.player_total == 11:  # A,9
                if dealer_upcard in [2, 3, 4, 5, 6]:  # Dealer upcard 2-6
                    return "stand"
                else:
                    return "stand"
            elif self.player_total == 10:  # A,8
                return "stand"
            elif self.player_total == 9:  # A,7
                if dealer_upcard in [3, 4, 5, 6]:  # Dealer upcard 3-6
                    return "double stand"
                elif dealer_upcard in [2, 7, 8]:
                    return "stand"
                else:
                    return "hit"
            elif self.player_total == 8:  # A,6
                if dealer_upcard in [3, 4, 5, 6]:
                    return "double hit"
                else:
                    return "hit"
            elif self.player_total == 7:  # A,5
                if dealer_upcard in [4, 5, 6]:
                    return "double hit"
                else:
                    return "hit"
            elif self.player_total == 6:  # A,4
                if dealer_upcard in [4, 5, 6]:
                    return "double hit"
                else:
                    return "hit"
            elif self.player_total == 5:  # A,3
                if dealer_upcard in [5, 6]:
                    return "double hit"
                else:
                    return "hit"
            elif self.player_total == 4:  # A,2
                if dealer_upcard in [5, 6]:
                    return "double hit"
                else:
                    return "hit"
        
        # Hard totals logic
        else:
            if self.player_total >= 17:  # 17 or higher
                return "stand"
            elif self.player_total == 16:
                if dealer_upcard in [2, 3, 4, 5, 6]:
                    return "stand"
                else:
                    return "hit"
            elif self.player_total == 15:
                if dealer_upcard in [2, 3, 4, 5, 6]:
                    return "stand"
                else:
                    return "hit"
            elif self.player_total == 14:
                if dealer_upcard in [2, 3, 4, 5, 6]:
                    return "stand"
                else:
                    return "hit"
            elif self.player_total == 13:
                if dealer_upcard in [2, 3, 4, 5, 6]:
                    return "stand"
                else:
                    return "hit"
            elif self.player_total == 12:
                if dealer_upcard in [4, 5, 6]:
                    return "stand"
                else:
                    return "hit"
            elif self.player_total == 11:
                return "double hit"
            elif self.player_total == 10:
                if dealer_upcard in [2, 3, 4, 5, 6, 7, 8, 9]:
                    return "double hit"
                else:
                    return "hit"
            elif self.player_total == 9:
                if dealer_upcard in [3, 4, 5, 6]:
                    return "double hit"
                else:
                    return "hit"
            else:  # 8 or less
                return "hit"
            
            
        def split_decision(self):
            pass
        
        def double_decision(self):
            pass
        
        def hit_decision(self):
            pass
        
        def stand_decision(self):
            pass
        
