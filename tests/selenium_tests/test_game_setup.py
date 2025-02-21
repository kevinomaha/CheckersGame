import pytest
from .page_objects.game_page import GamePage

def test_initial_board_setup(driver):
    game_page = GamePage(driver)
    game_page.navigate_to()
    
    # Verify initial player is red
    assert game_page.get_current_player() == "red"
    
    # Verify initial piece counts
    assert game_page.get_piece_count("red") == 12
    assert game_page.get_piece_count("black") == 12

def test_game_board_rendered(driver):
    game_page = GamePage(driver)
    game_page.navigate_to()
    
    # Verify all squares are rendered
    for row in range(8):
        for col in range(8):
            assert game_page.get_square(row, col).is_displayed()

def test_new_game_button(driver):
    game_page = GamePage(driver)
    game_page.navigate_to()
    
    # Start a new game
    game_page.new_game()
    
    # Verify board is reset
    assert game_page.get_current_player() == "red"
    assert game_page.get_piece_count("red") == 12
    assert game_page.get_piece_count("black") == 12
