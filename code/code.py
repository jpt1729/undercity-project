# Raspberry Pi Pico

import board,busio # type: ignore
from time import sleep
from adafruit_st7735r import ST7735R
import displayio
import terminalio
from adafruit_display_text import label
import fourwire
import time

from digitalio import DigitalInOut, Direction, Pull

import rotaryio

from cards import *
import pokerlib as pokerlib

# Initialize poker calculator
poker_calc = pokerlib.PokerCalculator()

encoder = rotaryio.IncrementalEncoder(board.GP14, board.GP15)
last_position = None

btn = DigitalInOut(board.GP11)
btn.direction = Direction.INPUT
btn.pull = Pull.UP


mosi_pin = board.GP19
clk_pin = board.GP18
reset_pin = board.GP20
cs_pin = board.GP17
dc_pin = board.GP16

displayio.release_displays()

spi = busio.SPI(clock=clk_pin, MOSI=mosi_pin)

display_bus = fourwire.FourWire(spi, command=dc_pin, chip_select=cs_pin, reset=reset_pin)

display = ST7735R(display_bus, width=128, height=160, bgr = True)

splash = displayio.Group()
display.root_group = splash

color_bitmap = displayio.Bitmap(128, 160, 1)

color_palette = displayio.Palette(1)
color_palette[0] = 0x000000  # Black background

bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
splash.append(bg_sprite)

# Create title at the top
title_group = displayio.Group(scale=1, x=50, y=10)
title_text = "Poker"
title_area = label.Label(terminalio.FONT, text=title_text, color=0x00FF00)
title_group.append(title_area)
splash.append(title_group)


# Create percentage display in the middle
percentage_group = displayio.Group(scale=1, x=64, y=130)
percentage_text = "0%"
percentage_area = label.Label(terminalio.FONT, text=percentage_text, color=0xFFFF00)
percentage_group.append(percentage_area)
splash.append(percentage_group)

def calculate_win_percentage():
    """Calculate and display win percentage based on current cards"""
    # Only calculate if we have both hole cards
    if suit is not None and rank is not None and suit2 is not None and rank2 is not None:
        player_cards = []
        community_cards = []
        
        suit_lower = suit.lower()
        player_cards.append(f"{suit_lower}{rank}")
        
        suit2_lower = suit2.lower()
        player_cards.append(f"{suit2_lower}{rank2}")
        
        # Add community cards if both suit and rank are set
        for i in range(5):
            if river_suits[i] is not None and river_ranks[i] is not None:
                suit_lower = river_suits[i].lower()
                community_cards.append(f"{suit_lower}{river_ranks[i]}")
        
        # Calculate win probability against 3 opponents
        win_prob = poker_calc.calculate_win_probability(
            player_cards, community_cards, num_opponents=3, simulations=10
        )
        percentage_text = f"{win_prob:.0%}"
        percentage_area.text = percentage_text

# Create suit and rank selection areas
suit_group = displayio.Group(scale=1, x=40, y=120)
suit_text = "_"
suit_area = label.Label(terminalio.FONT, text=suit_text, color=0xFFFF00)
suit_group.append(suit_area)
splash.append(suit_group)

rank_group = displayio.Group(scale=1, x=46, y=120)
rank_text = "_"
rank_area = label.Label(terminalio.FONT, text=rank_text, color=0xFFFF00)
rank_group.append(rank_area)
splash.append(rank_group)

suit2_group = displayio.Group(scale=1, x=82, y=120)
suit2_text = "_"
suit2_area = label.Label(terminalio.FONT, text=suit2_text, color=0xFFFF00)
suit2_group.append(suit2_area)
splash.append(suit2_group)

rank2_group = displayio.Group(scale=1, x=88, y=120)
rank2_text = "_"
rank2_area = label.Label(terminalio.FONT, text=rank2_text, color=0xFFFF00)
rank2_group.append(rank2_area)
splash.append(rank2_group)


# Create 5 river card selection areas at the top
river_cards = []
river_x_positions = [15, 35, 55, 75, 95]
for i in range(5):
    # Create suit underscore for this card
    river_suit_group = displayio.Group(scale=1, x=river_x_positions[i], y=20)
    river_suit_text = "_"
    river_suit_area = label.Label(terminalio.FONT, text=river_suit_text, color=0xFFFFFF)
    river_suit_group.append(river_suit_area)
    splash.append(river_suit_group)
    
    # Create rank underscore for this card
    river_rank_group = displayio.Group(scale=1, x=river_x_positions[i] + 6, y=20)
    river_rank_text = "_"
    river_rank_area = label.Label(terminalio.FONT, text=river_rank_text, color=0xFFFFFF)
    river_rank_group.append(river_rank_area)
    splash.append(river_rank_group)
    

    river_cards.append({
        'suit': river_suit_area,
        'rank': river_rank_area
    })

# Flashing function
def make_text_flash(label, flash_interval=0.5, visible_color=0xFFFF00, invisible_color=0x000000):
    """
    Make a text label flash
    
    Args:
        label: The label to flash
        flash_interval: Time between flashes in seconds
        visible_color: Color when visible
        invisible_color: Color when invisible
    """
    flash_time = time.monotonic()
    flash_visible = True
    
    def update_flash():
        nonlocal flash_time, flash_visible
        current_time = time.monotonic()
        
        if current_time - flash_time >= flash_interval:
            flash_visible = not flash_visible
            flash_time = current_time
            label.color = visible_color if flash_visible else invisible_color
    
    return update_flash

flash_interval = 0.2

# Create flashing functions for suit and rank
update_suit_flash = make_text_flash(suit_area, flash_interval=flash_interval)
update_rank_flash = make_text_flash(rank_area, flash_interval=flash_interval)
update_suit2_flash = make_text_flash(suit2_area, flash_interval=flash_interval)
update_rank2_flash = make_text_flash(rank2_area, flash_interval=flash_interval)


# Create flashing functions for river cards
river_suit_flashes = []
river_rank_flashes = []
for i in range(5):
    river_suit_flashes.append(
        make_text_flash(river_cards[i]['suit'], 
                        flash_interval=flash_interval, 
                        visible_color=0xFFFFFF,
                        invisible_color=0x000000)
                    )
    river_rank_flashes.append(
        make_text_flash(river_cards[i]['rank'], 
                        flash_interval=flash_interval, 
                        visible_color=0xFFFFFF,
                        invisible_color=0x000000)
                    )

suit = None
rank = None
suit2 = None
rank2 = None

# River card states - each card has suit and rank
river_suits = [None] * 5
river_ranks = [None] * 5

# Track used cards to prevent duplicates
used_cards = set()

# Track what we were selecting last time to detect new selections
last_selection = None
last_card_index = None

last_btn_state = True  # Track button state for debouncing

def stop_other_flashing(current_card_index = None, current_selection = None):
    """Stop all cards from flashing and set them to their normal colors"""
    # Always set hand cards to yellow (unless they're currently being selected)
    if not (current_selection == "suit" and current_card_index == 0):
        suit_area.color = 0xFFFF00
    if not (current_selection == "rank" and current_card_index == 0):
        rank_area.color = 0xFFFF00
    if not (current_selection == "suit" and current_card_index == 1):
        suit2_area.color = 0xFFFF00
    if not (current_selection == "rank" and current_card_index == 1):
        rank2_area.color = 0xFFFF00

    # Set river cards to white (unless they're currently being selected)
    for i in range(5):
        if i != current_card_index:
            river_cards[i]['suit'].color = 0xFFFFFF
            river_cards[i]['rank'].color = 0xFFFFFF

def reset_all_cards():
    """Reset all cards and used_cards set"""
    global suit, rank, suit2, rank2, river_suits, river_ranks, used_cards
    
    # Reset hand cards
    suit = None
    rank = None
    suit2 = None
    rank2 = None
    
    # Reset river cards
    river_suits = [None] * 5
    river_ranks = [None] * 5
    
    # Clear used cards
    used_cards.clear()
    
    # Reset display text
    suit_area.text = "_"
    rank_area.text = "_"
    suit2_area.text = "_"
    rank2_area.text = "_"
    
    for i in range(5):
        river_cards[i]['suit'].text = "_"
        river_cards[i]['rank'].text = "_"
    
    # Reset percentage
    percentage_area.text = "0%"
    
    print("All cards reset!")

def determine_current_selection():
    current_selection = None
    current_card_index = None
    
    if suit == None:
        current_selection = "suit"
        current_card_index = 0
    elif rank == None:
        current_selection = "rank"
        current_card_index = 0
    elif suit2 == None:
        current_selection = "suit"
        current_card_index = 1
    elif rank2 == None:
        current_selection = "rank"
        current_card_index = 1
    else:
        # Check river cards
        for i in range(5):
            if river_suits[i] == None:
                current_selection = "river_suit"
                current_card_index = i
                break
            elif river_ranks[i] == None:
                current_selection = "river_rank"
                current_card_index = i
                break
    return current_selection, current_card_index

while True:
    # Determine what we're currently selecting
    current_selection, current_card_index = determine_current_selection()
    
    # Update flashing based on what we're selecting
    if current_selection == "suit" and current_card_index == 0:
        update_suit_flash()
        # Stop all others from flashing
        stop_other_flashing(current_card_index, current_selection)

    elif current_selection == "rank" and current_card_index == 0:
        update_rank_flash()
        # Stop all others from flashing
        stop_other_flashing(current_card_index, current_selection)

    elif current_selection == "suit" and current_card_index == 1:
        update_suit2_flash()
        # Stop all others from flashing
        stop_other_flashing(current_card_index, current_selection)

    elif current_selection == "rank" and current_card_index == 1:
        update_rank2_flash()
        # Stop all others from flashing
        stop_other_flashing(current_card_index, current_selection)

    elif current_selection == "river_suit":
        river_suit_flashes[current_card_index]()
        # Stop all others from flashing
        stop_other_flashing(current_card_index)

    elif current_selection == "river_rank":
        river_rank_flashes[current_card_index]()
        # Stop all others from flashing
        stop_other_flashing(current_card_index)

    else:
        stop_other_flashing()

    position = encoder.position
    
    if (current_selection != last_selection or current_card_index != last_card_index) and current_selection is not None:
        if current_selection == "suit" and current_card_index == 0:
            suit_area.text = select_suit(position, used_cards)
        elif current_selection == "rank" and current_card_index == 0:
            rank_area.text = select_rank(position, suit, used_cards)
        elif current_selection == "suit" and current_card_index == 1:
            suit2_area.text = select_suit(position, used_cards)
        elif current_selection == "rank" and current_card_index == 1:
            rank2_area.text = select_rank(position, suit2, used_cards)
        elif current_selection == "river_suit":
            river_cards[current_card_index]['suit'].text = select_suit(position, used_cards)
        elif current_selection == "river_rank":
            river_cards[current_card_index]['rank'].text = select_rank(position, river_suits[current_card_index], used_cards)
    
    if last_position is None or position != last_position:
        if current_selection == "suit" and current_card_index == 0:
            suit_area.text = select_suit(position, used_cards)
        elif current_selection == "rank" and current_card_index == 0:
            rank_area.text = select_rank(position, suit, used_cards)
        elif current_selection == "suit" and current_card_index == 1:
            suit2_area.text = select_suit(position, used_cards)
        elif current_selection == "rank" and current_card_index == 1:
            rank2_area.text = select_rank(position, suit2, used_cards)
        elif current_selection == "river_suit":
            river_cards[current_card_index]['suit'].text = select_suit(position, used_cards)
        elif current_selection == "river_rank":
            river_cards[current_card_index]['rank'].text = select_rank(position, river_suits[current_card_index], used_cards)
    last_position = position
    
    # Update tracking variables
    last_selection = current_selection
    last_card_index = current_card_index
    
    # Button handling with debouncing
    current_btn_state = btn.value
    if last_btn_state and not current_btn_state:
        # Check if all cards are selected (reset condition)
        if current_selection is None:
            reset_all_cards()
        elif current_selection == "suit" and current_card_index == 0:
            suit = select_suit(position, used_cards)
            print(f"Card 1 suit set to: {suit}")
        elif current_selection == "rank" and current_card_index == 0:
            rank = select_rank(position, suit, used_cards)
            used_cards.add((suit, rank))
            print(f"Card 1 rank set to: {rank}")
        elif current_selection == "suit" and current_card_index == 1:
            suit2 = select_suit(position, used_cards)
            print(f"Card 2 suit set to: {suit2}")
        elif current_selection == "rank" and current_card_index == 1:
            rank2 = select_rank(position, suit2, used_cards)
            used_cards.add((suit2, rank2))
            print(f"Card 2 rank set to: {rank2}")
            calculate_win_percentage()
        elif current_selection == "river_suit":
            river_suits[current_card_index] = select_suit(position, used_cards)
            print(f"River card {current_card_index + 1} suit set to: {river_suits[current_card_index]}")
        elif current_selection == "river_rank":
            river_ranks[current_card_index] = select_rank(position, river_suits[current_card_index], used_cards)
            used_cards.add((river_suits[current_card_index], river_ranks[current_card_index]))
            print(f"River card {current_card_index + 1} rank set to: {river_ranks[current_card_index]}")
            # Only calculate after flop (3 cards), turn (4th card), and river (5th card)
            if current_card_index >= 2: 
                calculate_win_percentage()
    last_btn_state = current_btn_state
    
    sleep(0.0010)  # 10ms delay