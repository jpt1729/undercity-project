def select_suit(selection, used_cards=None):
    suits = ['h', 'd', 'c', 's']
    if used_cards is None:
        return suits[selection % len(suits)]
    
    # Filter out suits that have no available ranks
    available_suits = []
    for suit in suits:
        for rank in ['A', 'K', 'Q', 'J', '10', '9', '8', '7', '6', '5', '4', '3', '2', '1']:
            if (suit, rank) not in used_cards:
                available_suits.append(suit)
                break
    
    if not available_suits:
        return suits[0]  # Fallback if all cards are used
    
    return available_suits[selection % len(available_suits)]

def select_rank(selection, suit, used_cards=None):
    ranks = ['A', 'K', 'Q', 'J', '10', '9', '8', '7', '6', '5', '4', '3', '2', '1']
    if used_cards is None:
        return ranks[selection % len(ranks)]
    
    # Filter out ranks that are already used with this suit
    available_ranks = []
    for rank in ranks:
        if (suit, rank) not in used_cards:
            available_ranks.append(rank)
    
    if not available_ranks:
        return ranks[0]  # Fallback if all ranks are used for this suit
    
    return available_ranks[selection % len(available_ranks)]

def set_hand(encoder, last_position, btn, suit, rank):
    position = encoder.position
    if last_position is None or position != last_position:
        if suit == None:
            encoder_area.text = f"{select_suit(position)}_"
        else:
            encoder_area.text = f"{suit}{select_rank(position)}"
    last_position = position
    if not btn.value:
        suit = select_suit(position)