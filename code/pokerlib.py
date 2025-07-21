import random

class PokerCalculator:
    def __init__(self):
        # Card ranks and suits
        self.ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.suits = ['h', 'd', 'c', 's']  # hearts, diamonds, clubs, spades
        
        # Hand rankings (higher number = better hand)
        self.hand_rankings = {
            'high_card': 1,
            'pair': 2,
            'two_pair': 3,
            'three_of_a_kind': 4,
            'straight': 5,
            'flush': 6,
            'full_house': 7,
            'four_of_a_kind': 8,
            'straight_flush': 9,
            'royal_flush': 10
        }
    
    def create_deck(self, exclude_cards=None):
        """Create a deck excluding specified cards"""
        if exclude_cards is None:
            exclude_cards = []
        
        deck = []
        for suit in self.suits:
            for rank in self.ranks:
                card = f"{suit}{rank}"
                if card not in exclude_cards:
                    deck.append(card)
        return deck
    
    def get_all_combinations(self, cards, r):
        """Get all combinations of r cards from the list (without itertools)"""
        if r == 0:
            return [[]]
        if len(cards) < r:
            return []
        
        result = []
        for i in range(len(cards) - r + 1):
            for combo in self.get_all_combinations(cards[i+1:], r-1):
                result.append([cards[i]] + combo)
        return result
    
    def evaluate_hand(self, cards):
        """Evaluate a 5-card hand and return its rank"""
        if len(cards) != 5:
            return 0, 'invalid'
        
        # Parse cards
        ranks = []
        suits = []
        for card in cards:
            if len(card) == 3:  # h10, d10, etc.
                suits.append(card[0])
                ranks.append(card[1:])
            else:  # hA, dK, etc.
                suits.append(card[0])
                ranks.append(card[1])
        
        # Count occurrences
        rank_counts = {}
        for rank in ranks:
            rank_counts[rank] = rank_counts.get(rank, 0) + 1
        
        suit_counts = {}
        for suit in suits:
            suit_counts[suit] = suit_counts.get(suit, 0) + 1
        
        # Check for flush
        is_flush = max(suit_counts.values()) == 5
        
        # Check for straight
        rank_values = [self.ranks.index(rank) for rank in ranks]
        rank_values.sort()
        is_straight = (max(rank_values) - min(rank_values) == 4 and len(set(rank_values)) == 5) or \
                     (set(rank_values) == {0, 1, 2, 3, 12})  # A-2-3-4-5 straight
        
        # Determine hand type
        if is_straight and is_flush:
            if min(rank_values) == 8:  # A-high straight flush
                return 10, 'royal_flush'
            else:
                return 9, 'straight_flush'
        elif max(rank_counts.values()) == 4:
            return 8, 'four_of_a_kind'
        elif sorted(rank_counts.values()) == [2, 3]:
            return 7, 'full_house'
        elif is_flush:
            return 6, 'flush'
        elif is_straight:
            return 5, 'straight'
        elif max(rank_counts.values()) == 3:
            return 4, 'three_of_a_kind'
        elif list(rank_counts.values()).count(2) == 2:
            return 3, 'two_pair'
        elif max(rank_counts.values()) == 2:
            return 2, 'pair'
        else:
            return 1, 'high_card'
    
    def get_best_hand(self, hole_cards, community_cards):
        """Get the best 5-card hand from hole cards and community cards"""
        all_cards = hole_cards + community_cards
        if len(all_cards) < 5:
            return 0, 'not_enough_cards'
        
        best_hand = 0
        best_hand_type = 'high_card'
        
        # Try all combinations of 5 cards
        for combo in self.get_all_combinations(all_cards, 5):
            hand_value, hand_type = self.evaluate_hand(combo)
            if hand_value > best_hand:
                best_hand = hand_value
                best_hand_type = hand_type
        
        return best_hand, best_hand_type
    
    def calculate_win_probability(self, player_hole_cards, community_cards, num_opponents=1, simulations=100):
        """
        Calculate probability of winning given:
        - player_hole_cards: list of 2 cards (e.g., ['hA', 'dK'])
        - community_cards: list of community cards (e.g., ['h7', 'd8', 'c9'])
        - num_opponents: number of opponents
        - simulations: number of Monte Carlo simulations
        """
        wins = 0
        
        for _ in range(simulations):
            # Create deck excluding known cards
            known_cards = player_hole_cards + community_cards
            deck = self.create_deck(known_cards)
            
            # Deal random hole cards to opponents
            opponent_hands = []
            for _ in range(num_opponents):
                if len(deck) >= 2:
                    # Use random.choice instead of random.sample
                    card1 = random.choice(deck)
                    deck.remove(card1)
                    card2 = random.choice(deck)
                    deck.remove(card2)
                    opponent_hole = [card1, card2]
                    opponent_hands.append(opponent_hole)
            
            # Complete the community cards if needed
            remaining_community = 5 - len(community_cards)
            if remaining_community > 0 and len(deck) >= remaining_community:
                additional_community = []
                for _ in range(remaining_community):
                    card = random.choice(deck)
                    deck.remove(card)
                    additional_community.append(card)
                final_community = community_cards + additional_community
            else:
                final_community = community_cards
            
            # Evaluate all hands
            player_hand_value, player_hand_type = self.get_best_hand(player_hole_cards, final_community)
            
            # Check if player wins
            player_wins = True
            for opponent_hole in opponent_hands:
                opponent_hand_value, opponent_hand_type = self.get_best_hand(opponent_hole, final_community)
                if opponent_hand_value > player_hand_value:
                    player_wins = False
                    break
            
            if player_wins:
                wins += 1
        
        return wins / simulations
    
    def format_cards(self, cards):
        """Format cards for display"""
        return ' '.join(cards)

# Example usage and testing
if __name__ == "__main__":
    calc = PokerCalculator()
    
    # Example: Pocket aces vs random hands
    player_cards = ['hA', 'dA']  # Pocket aces
    community_cards = ['h7', 'd8', 'c9']  # Flop
    
    print(f"Player hole cards: {calc.format_cards(player_cards)}")
    print(f"Community cards: {calc.format_cards(community_cards)}")
    
    # Calculate win probability against 1 opponent
    win_prob = calc.calculate_win_probability(player_cards, community_cards, num_opponents=1, simulations=100)
    print(f"Win probability: {win_prob:.1%}")
    
    # Calculate win probability against 3 opponents
    win_prob_3 = calc.calculate_win_probability(player_cards, community_cards, num_opponents=3, simulations=100)
    print(f"Win probability vs 3 opponents: {win_prob_3:.1%}") 