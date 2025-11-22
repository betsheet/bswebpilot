import random
import time

import undetected_chromedriver as uc  # TODO: mirar v2 https://pypi.org/project/undetected-chromedriver/2.1.1/
from selenium.common import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bswebpilot.bswebpilot.utils.locator import BSLocator


class BSWebDriver:
    driver: uc.Chrome
    options: uc.ChromeOptions

    # Settings
    medium_waiting_time: float = 15.0  # para esperas explícitas
    short_waiting_time: float = 2.0  # para búsqueda de elementos
    min_human_typing_wait: float = 0.04
    max_human_typing_wait: float = 0.19

    def __init__(self, is_headless: bool = False):
        self.options = uc.ChromeOptions()
        self.options.add_argument("--incognito")
        if is_headless:
            self.headless()
        self.driver = uc.Chrome(self.options)
        self.driver.execute_cdp_cmd(
            "Network.setUserAgentOverride", {
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"}
        )

    def quit(self):
        self.driver.quit()

    def close_tab(self, window_handle: str):
        # TODO
        pass

    def headless(self) -> None:
        self.options.add_argument("--headless")
        """self.driver.execute_cdp_cmd(
            "Network.setUserAgentOverride", {
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"}
        )"""

    def set_implicit_wait(self, wait_time: float) -> None:
        self.driver.implicitly_wait(wait_time)

    def navigate_to(self, url: str) -> None:
        self.driver.get(url)

    def maximize_window(self) -> None:
        self.driver.maximize_window()

    def grab_focus(self) -> None:
        self.driver.execute_script("window.focus();")

    # Elements
    def find_element(self, locator: BSLocator, retry: bool = False) -> WebElement:
        try:
            return self.driver.find_element(locator.by, locator.value)
        except NoSuchElementException as e:
            if not retry:
                raise e
            return self.find_element(locator, False)

    def find_elements(self, locator: BSLocator, retry: bool = False):
        elements: list[WebElement] = self.driver.find_elements(locator.by, locator.value)
        if not bool(elements) and retry:
            elements = self.find_elements(locator, False)
        return elements

    def click_element(self, locator: BSLocator) -> None:
        self.wait_element_to_be_clickable(locator)
        self.find_element(locator).click()

    def clear(self, locator: BSLocator):
        self.wait_element_to_be_clickable(locator)
        self.find_element(locator).clear()

    def send_keys(self, locator: BSLocator, content: str):
        self.wait_element_to_be_present(locator)
        self.find_element(locator).send_keys(content)

    def clear_and_send_keys(self, locator: BSLocator, content: str):
        self.clear(locator)
        self.send_keys(locator, content)

    def human_type(self, locator: BSLocator, content: str):
        self.wait_element_to_be_clickable(locator)
        elem = self.find_element(locator)
        time.sleep(random.uniform(self.min_human_typing_wait, self.max_human_typing_wait))
        for char in str(content):
            elem.send_keys(char)
            time.sleep(random.uniform(self.min_human_typing_wait, self.max_human_typing_wait))

    def clear_and_human_type(self, locator: BSLocator, content: str):
        self.wait_random(self.min_human_typing_wait, self.max_human_typing_wait)
        self.clear(locator)
        self.wait_random(self.min_human_typing_wait, self.max_human_typing_wait)
        self.human_type(locator, content)

    def get_text(self, locator: BSLocator, raise_exception: bool = False, timeout=10) -> str:
        self.wait_element_to_be_visible(locator, raise_exception, timeout)
        try:
            return self.find_element(locator).text
        except TimeoutException as e:
            if raise_exception: raise e

    def get_class(self, locator: BSLocator) -> str:
        self.wait_element_to_be_present(locator)
        return self.find_element(locator).get_attribute("class").strip()

    def get_value(self, locator: BSLocator) -> str:
        self.wait_element_to_be_present(locator)
        return self.find_element(locator).get_attribute("value").strip()

    # Presence of elements
    def is_element_present(self, locator: BSLocator, tolerance_time: float = 10):
        try:
            WebDriverWait(self.driver, tolerance_time).until(EC.presence_of_element_located(locator.as_tuple()))
            return True
        except TimeoutException:
            return False

    def is_element_displayed(self, locator: BSLocator, tolerance_time: float = 10):
        return self.is_element_present(locator, tolerance_time) and self.find_element(locator).is_displayed()

    def is_element_clickable(self, locator: BSLocator, tolerance_time: float = 10):
        try:
            WebDriverWait(self.driver, tolerance_time).until(EC.element_to_be_clickable(locator.as_tuple()))
            return True
        except TimeoutException:
            return False
        except ElementClickInterceptedException:
            return False

    # Explicit waits
    # TODO: añadir opción para generar o no excepción
    def wait_element_to_be_present(self, locator: BSLocator, tolerance_time: float = 10):
        WebDriverWait(self.driver, tolerance_time).until(EC.presence_of_element_located(locator.as_tuple()))

    def wait_element_to_be_clickable(self, locator: BSLocator, tolerance_time: float = 10,
                                     raise_exception: bool = True):
        try:
            WebDriverWait(self.driver, tolerance_time).until(EC.element_to_be_clickable(locator.as_tuple()))
        except TimeoutException as e:
            if raise_exception:
                raise e

    def wait_element_to_be_visible(self, locator: BSLocator, raise_exception: bool = True, tolerance_time: float = 10):
        try:
            WebDriverWait(self.driver, tolerance_time).until(EC.visibility_of_element_located(locator.as_tuple()))
        except TimeoutException as e:
            if raise_exception:
                raise e
                # TODO: replicar esto en todos los waits que lanzan excepción.

    def wait_element_to_be_invisible(self, locator: BSLocator, raise_exception: bool = False, tolerance_time: float = 10):
        try:
            WebDriverWait(self.driver, tolerance_time).until(EC.invisibility_of_element_located(locator.as_tuple()))
        except TimeoutException as e:
            if raise_exception: raise e

    def wait_page_to_be_loaded(self, max_time: float = 10):
        WebDriverWait(self.driver, max_time).until(
            lambda d: d.execute_script("return document.readyState") == "complete")

    def wait_element_class_to_contain(self, locator: BSLocator, content: str, max_time: float = 10):
        WebDriverWait(self.driver, max_time).until(
            lambda d: content in self.find_element(locator).get_attribute("class"))

    def wait_attribute_to_contain(self, locator: BSLocator, attr: str, content: str, tolerance_time: float = 10, raise_exception: bool = False):
        try:
            WebDriverWait(self.driver, tolerance_time).until(
                lambda d: content in self.find_element(locator).get_attribute(attr))
        except Exception as e:
            if raise_exception: raise e
    # Aux
    def get_current_url(self) -> str:
        return self.driver.current_url

    def scroll_element_into_view(self, element_locator: BSLocator):
        element: WebElement = self.find_element(element_locator)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)

    def scroll_to_page_top(self) -> None:
        self.execute_script("window.scrollTo(0, 0);")

    def execute_script(self, script: str) -> None:
        self.driver.execute_script(script)

    def save_screenshot(self, file_path: str = "screenshot.png"):
        self.driver.save_screenshot(file_path)

    def save_element_screenshot(self, element_locator: BSLocator, file_path: str = "screenshot.png"):
        self.find_element(element_locator).screenshot(file_path)

    @staticmethod
    def wait_random(_min: float, _max: float) -> None:
        time.sleep(random.uniform(_min, _max))

    @staticmethod
    def wait_static(wait_time: float) -> None:
        time.sleep(wait_time)
