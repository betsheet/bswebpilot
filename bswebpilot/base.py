import asyncio
import random
import time
from abc import ABC, abstractmethod

from bswebpilot.utils.locator import BSLocator


class BSWebPilot(ABC):

    def __init__(self, is_headless: bool = False, window_resolution: tuple[int, int] | None = None):
        self.is_headless = is_headless
        self.window_resolution = window_resolution

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
    def click(self, locator: BSLocator, timeout: float = 10) -> None:
        pass

    @abstractmethod
    def click_nth(self, locator: BSLocator, timeout: float = 10) -> None:
        pass

    @abstractmethod
    def manual_click_element(self, locator: BSLocator, timeout: float = 10) -> None:
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
    def clear_and_human_type(self, locator: BSLocator, value: str) -> None:
        pass

    @abstractmethod
    def get_element_text(self, locator: BSLocator, unsafe_mode: bool = True, timeout=10) -> str | None:
        pass

    @abstractmethod
    def get_elements_text(self, locator: BSLocator, timeout: float = 10) -> list[str]:
        pass

    @abstractmethod
    def get_attribute_value(self, locator: BSLocator, attribute: str) -> str:
        pass

    @abstractmethod
    def get_elements_count(self, locator: BSLocator, timeout: float = 10) -> int:
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
    def wait_element_to_be_present(self, locator: BSLocator, timeout: float = 10) -> None:
        pass

    @abstractmethod
    def wait_element_to_be_visible(self, locator: BSLocator, timeout: float = 10) -> None:
        pass

    @abstractmethod
    def wait_element_to_be_invisible(self, locator: BSLocator, timeout: float = 10) -> None:
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
    def wait(wait_time: float) -> None:
        time.sleep(wait_time)

    @abstractmethod
    def save_screenshot(self, output_path: str) -> None:
        pass


class BSWebPilotAsync(ABC):

    def __init__(self, is_headless: bool = False, window_resolution: tuple[int, int] | None = None):
        self.is_headless = is_headless
        self.window_resolution = window_resolution

    @abstractmethod
    async def initialize(self) -> None:
        pass

    @abstractmethod
    async def quit(self) -> None:
        pass

    @abstractmethod
    async def navigate_to(self, url: str) -> None:
        pass

    @abstractmethod
    async def get_current_url(self) -> str:
        pass

    @abstractmethod
    async def click(self, locator: BSLocator, timeout: float = 10) -> None:
        pass

    @abstractmethod
    async def click_nth(self, locator: BSLocator, index: int, timeout: float = 10) -> None:
        pass

    @abstractmethod
    async def manual_click(self, locator: BSLocator, timeout: float = 10) -> None:
        pass

    @abstractmethod
    async def clear(self, locator: BSLocator) -> None:
        pass

    @abstractmethod
    async def human_type(self, locator: BSLocator, text: str, timeout: float = 10) -> None:
        pass

    @abstractmethod
    async def clear_and_human_type(self, locator: BSLocator, value: str) -> None:
        pass

    @abstractmethod
    async def get_element_text(self, locator: BSLocator, timeout: float = 10, raise_exception: bool = True) -> str | None:
        pass

    @abstractmethod
    async def get_elements_text(self, locator: BSLocator, timeout: float = 10) -> list[str]:
        pass

    @abstractmethod
    async def get_attribute_value(self, locator: BSLocator, attr: str, timeout: float = 10) -> str | None:
        pass

    @abstractmethod
    async def get_elements_count(self, locator: BSLocator, timeout: float = 10) -> int:
        pass

    @abstractmethod
    async def is_element_present(self, locator: BSLocator, timeout: float = 10) -> bool:
        pass

    @abstractmethod
    async def is_element_not_present(self, locator: BSLocator, timeout: float = 10) -> bool:
        pass

    @abstractmethod
    async def is_element_visible(self, locator: BSLocator, timeout: float = 10) -> bool:
        pass

    @abstractmethod
    async def wait_element_to_be_present(self, locator: BSLocator, timeout: float = 10) -> None:
        pass

    @abstractmethod
    async def wait_element_to_be_visible(self, locator: BSLocator, timeout: float = 10) -> None:
        pass

    @abstractmethod
    async def wait_element_to_be_invisible(self, locator: BSLocator, timeout: float = 10) -> None:
        pass

    @abstractmethod
    async def wait_page_to_be_loaded(self, timeout: float = 10) -> None:
        pass

    @abstractmethod
    async def scroll_element_into_view(self, locator: BSLocator, timeout: float = 10) -> None:
        pass

    @abstractmethod
    async def save_screenshot(self, output_path: str) -> None:
        pass

    @staticmethod
    async def wait_random(_min: float, _max: float) -> None:
        await asyncio.sleep(random.uniform(_min, _max))

    @staticmethod
    async def wait(wait_time: float) -> None:
        await asyncio.sleep(wait_time)

    @abstractmethod
    async def __aenter__(self) -> "BSWebPilotAsync":
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        pass

    def __del__(self) -> None:
        """Último recurso de limpieza. Usar quit() o el context manager explícitamente."""
        pass

