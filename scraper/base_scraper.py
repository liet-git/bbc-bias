from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from abc import ABC
from abc import abstractmethod


class Scraper(ABC):

    def __init__(self, service):

        self.service = service
        self.browser = None

    def wait_for_object(self, xpath, browser=None, wait_time=10):
        """
        Wait for selected xpath object to appear

        Args:
            xpath (str): xpath of the item we want to wait for
            browser (webdriver): webdriver object to use for scraping
            wait_time (int): time to wait for object in seconds

        Returns:
            element if it is present, otherwise none
        """

        if not browser:
            browser = self.browser

        element = WebDriverWait(browser, wait_time).until(EC.presence_of_element_located((By.XPATH, xpath)))

        if not element:
            return None

        return element

    def initialise_browser(self, options=None, browser=None):
        """
        Initialise browser instance (webdriver)

        Args:
            options (webdriver): options to use for our service
            browser (webdriver): initialised webdriver (such as webdriver.Chrome) to use
        """

        if not options:
            options = webdriver.ChromeOptions()
            options.add_argument('ignore-certificate-errors')
            options.add_argument("start-maximized")
            options.add_argument('--headless')
        if not browser:
            if not self.service: self.service = Service(ChromeDriverManager().install())
            self.browser = webdriver.Chrome(service=self.service, options=options)
        else:
            self.browser = browser

    @abstractmethod
    def return_entities(self):
        pass
