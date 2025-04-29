# src/browser/driver_setup.py

# 📦 Import required libraries
import chromedriver_autoinstaller  # Automatically installs matching ChromeDriver # type: ignore
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def get_driver():
    """
    Sets up and returns a Selenium Chrome WebDriver instance.

    - Auto-installs the correct ChromeDriver version.
    - Configures Chrome options for stealthy automation.
    - Returns a maximized, ready-to-use driver.
    
    Returns:
        webdriver.Chrome: Selenium WebDriver instance.
    """

    # 📥 Auto-install matching ChromeDriver version
    chromedriver_autoinstaller.install()

    # ⚙️ Set Chrome options
    options = Options()
    options.add_argument("--start-maximized")  # Start browser maximized
    options.add_argument("--disable-blink-features=AutomationControlled")  # Hide 'controlled by automation'
    options.add_experimental_option("excludeSwitches", ["enable-automation"])  # Remove automation switches
    options.add_experimental_option('useAutomationExtension', False)  # Disable automation extension

    # 🚀 Launch Chrome browser with these options
    driver = webdriver.Chrome(options=options)

    return driver
