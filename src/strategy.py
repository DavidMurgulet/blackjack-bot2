#rules, chosen by player.
double_down_ace= False
split_on = False
auto_bet = False


class Game:
    def __init__(self, cards, dealer_upcard):
        self.player_hand = cards
        self.dealer_hand = [dealer_upcard]
        self.player_total = sum(self.player_hand)
        self.split_games = []  
        self.dealer_upcard = dealer_upcard
        self.double_possible = False
        self.split_possible = False
        self.dealer_ace = False
        self.player_soft = False

        self.check_for_aces()

    def check_for_aces(self):
        if "11" in self.dealer_hand:
            self.dealer_ace = True

    def set_soft_hand(self, value):
        self.player_soft = value

    def new_card(self, card):
        self.player_hand.append(card)
        self.player_total = sum(self.player_hand)    

        if self.player_total > 21:
            return "bust"
        
        return self.make_decision()
    

    def make_decision(self):
        dealer_upcard = self.dealer_upcard

        if self.player_soft:
            return self._soft_hand_decision(dealer_upcard)
        else: 
            return self._hard_hand_decision(dealer_upcard)

    def _soft_hand_decision(self, dealer_upcard):
        if self.player_total == 20:  # 11,9
            return "stand"
        elif self.player_total == 19:  # 11,8
            return "stand"
        elif self.player_total == 18:  # 11,7
            if dealer_upcard in [3, 4, 5, 6]:  # Dealer upcard 3-6
                return "stand"
            elif dealer_upcard in [2, 7, 8]:
                return "stand"
            else:
                return "hit"
        elif self.player_total == 17:  # 11,6
            if dealer_upcard in [3, 4, 5, 6]:
                return "hit"
            else:
                return "hit"
        elif self.player_total == 16:  # 11,5
            if dealer_upcard in [4, 5, 6]:
                return "hit"
            else:
                return "hit"
        elif self.player_total == 15:  # 11,4
            if dealer_upcard in [4, 5, 6]:
                return "hit"
            else:
                return "hit"
        elif self.player_total == 14:  # 11,3
            if dealer_upcard in [5, 6]:
                return "hit"
            else:
                return "hit"
        elif self.player_total == 13:  # 11,2
            if dealer_upcard in [5, 6]:
                return "hit"
            else:
                return "hit"

    def _hard_hand_decision(self, dealer_upcard):
        """Logic for hard hands (no Ace or Ace counted as 1)."""
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
            return "hit"
        elif self.player_total == 10:
            if dealer_upcard in [2, 3, 4, 5, 6, 7, 8, 9]:
                return "hit"
            else:
                return "hit"
        elif self.player_total == 9:
            if dealer_upcard in [3, 4, 5, 6]:
                return "hit"
            else:
                return "hit"
        else:  # 8 or less
            return "hit"
