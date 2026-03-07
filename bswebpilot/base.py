from bswebpilot.utils.locator import BSLocator


class BSWebPilot:


    def __init__(self, is_headless: bool = False):
        pass

    def quit(self) -> None:
        pass

    def initialize(self) -> None:
        pass

    def maximize_window(self) -> None:
        pass

    def navigate_to(self, url: str) -> None:
        pass

    def click(self, locator: BSLocator) -> None:
        pass

    def click_js(self, locator: BSLocator) -> None:
        pass

    def clear(self, locator: BSLocator) -> None:
        pass

    def human_type(self, locator: BSLocator, text: str) -> None:
        pass

    def get_element_text(self, locator: BSLocator, unsafe_mode: bool = True, timeout=10) -> str | None:
        pass

    def get_element_attribute(self, locator: BSLocator, attribute: str) -> str:
        pass

    def is_element_present(self, locator: BSLocator, timeout: float = 10):
        pass