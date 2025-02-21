from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

class GamePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def navigate_to(self):
        self.driver.get("http://localhost:3001")
        # Wait for the page to load and click new game if needed
        try:
            new_game_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="new-game"]'))
            )
            new_game_button.click()
            time.sleep(2)  # Wait for game state to initialize
        except TimeoutException:
            raise Exception("Could not find or click the new game button")

    def get_square(self, row, col):
        try:
            return self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, f'[data-testid="square-{row}-{col}"]'))
            )
        except TimeoutException:
            raise Exception(f"Could not find square at row {row}, col {col}")

    def get_piece(self, row, col):
        try:
            return self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, f'[data-testid="piece-{row}-{col}"]'))
            )
        except TimeoutException:
            return None

    def make_move(self, from_row, from_col, to_row, to_col):
        try:
            from_square = self.get_square(from_row, from_col)
            from_square.click()
            time.sleep(1)  # Wait for valid moves to be highlighted
            
            to_square = self.get_square(to_row, to_col)
            to_square.click()
            time.sleep(1)  # Wait for move to complete
        except Exception as e:
            raise Exception(f"Failed to make move: {str(e)}")

    def get_current_player(self):
        try:
            element = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="current-player"]'))
            )
            return element.text.split(": ")[1].lower() if ": " in element.text else element.text.lower()
        except TimeoutException:
            raise Exception("Could not find current player indicator")

    def get_game_status(self):
        try:
            element = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="game-status"]'))
            )
            return element.text
        except TimeoutException:
            raise Exception("Could not find game status")

    def get_piece_count(self, color):
        pieces = self.driver.find_elements(By.CSS_SELECTOR, f'[data-testid^="piece-"][class*="{color}"]')
        return len(pieces)

    def new_game(self):
        new_game_button = self.driver.find_element(By.CSS_SELECTOR, '[data-testid="new-game"]')
        new_game_button.click()
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="piece-2-1"]')))
