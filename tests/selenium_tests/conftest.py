import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import chromedriver_autoinstaller

@pytest.fixture
def driver():
    # Install ChromeDriver if it's not already installed
    chromedriver_autoinstaller.install()
    
    # Create Chrome options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')  # Run in headless mode
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    # Initialize the driver
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    driver.maximize_window()
    
    yield driver
    driver.quit()
