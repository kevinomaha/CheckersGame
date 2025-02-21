import pytest
from .page_objects.game_page import GamePage

def test_valid_move(driver):
    game_page = GamePage(driver)
    game_page.navigate_to()
    
    # Make a valid move for red piece
    game_page.make_move(2, 1, 3, 2)
    
    # Verify player changed to black
    assert game_page.get_current_player() == "black"

def test_invalid_move(driver):
    game_page = GamePage(driver)
    game_page.navigate_to()
    
    # Attempt invalid move (moving to non-diagonal square)
    game_page.make_move(2, 1, 3, 1)
    
    # Verify player hasn't changed (still red's turn)
    assert game_page.get_current_player() == "red"

def test_capture_move(driver):
    game_page = GamePage(driver)
    game_page.navigate_to()
    
    # Setup for capture (need to make moves to create capture scenario)
    game_page.make_move(2, 1, 3, 2)  # Red moves
    game_page.make_move(5, 2, 4, 1)  # Black moves
    game_page.make_move(3, 2, 5, 0)  # Red captures black piece
    
    # Verify piece counts after capture
    assert game_page.get_piece_count("black") == 11
