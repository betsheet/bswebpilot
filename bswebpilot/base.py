import random
import time
from abc import ABC, abstractmethod

from bswebpilot.utils.locator import BSLocator


class BSWebPilot(ABC):


    def __init__(self, is_headless: bool = False, window_resolution: tuple[int, int] | None = None):
        self.is_headless = is_headless
        self.window_resolution = window_resolution

   # TODO: estos deberían ser los únicos métodos que se usaran desde los bots/scrappers

    @abstractmethod
    def initialize(self) -> None:
        pass

    @abstractmethod
    def quit(self) -> None:
        pass

    @abstractmethod
    def maximize_window(self) -> None:
        pass

    @abstractmethod
    def navigate_to(self, url: str) -> None:
        pass

    @abstractmethod
    def get_current_url(self) -> str:
        pass

    @abstractmethod
    def click(self, locator: BSLocator) -> None:
        pass

    @abstractmethod
    def click_js(self, locator: BSLocator) -> None:
        pass

    @abstractmethod
    def clear(self, locator: BSLocator) -> None:
        pass

    @abstractmethod
    def human_type(self, locator: BSLocator, text: str) -> None:
        pass

    @abstractmethod
    def get_element_text(self, locator: BSLocator, unsafe_mode: bool = True, timeout=10) -> str | None:
        pass

    @abstractmethod
    def get_element_attribute(self, locator: BSLocator, attribute: str) -> str:
        pass

    @abstractmethod
    def is_element_present(self, locator: BSLocator, timeout: float = 10) -> bool:
        pass

    @abstractmethod
    def is_element_not_present(self, locator: BSLocator, timeout: float = 10) -> bool:
        pass

    @abstractmethod
    def is_element_visible(self, locator: BSLocator, timeout: float = 10) -> bool:
        pass

    @abstractmethod
    def wait_element_to_be_present(self, locator: BSLocator, timeout: float = 10):
        pass
        pass

    @abstractmethod
    def wait_page_to_be_loaded(self, timeout: float = 10) -> None:
        pass

    @abstractmethod
    def scroll_element_into_view(self, locator: BSLocator, timeout: float = 10) -> None:
        pass

    @staticmethod
    def wait_random(_min: float, _max: float) -> None:
        time.sleep(random.uniform(_min, _max))

    @staticmethod
    def wait_static(wait_time: float) -> None:
        time.sleep(wait_time)

    @abstractmethod
    def save_screenshot(self, output_path: str) -> None:
        pass