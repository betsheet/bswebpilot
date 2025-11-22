from selenium.webdriver.common.by import By

class BSLocator:

    by : str    # TODO: deberíamos tener un enum By o locator_type para generalizar y no usar la nomenclatura de selenium
    value : str

    def __init__(self, by : str, value : str):
        self.by = by
        self.value = value

    def as_tuple(self) -> tuple[str, str]:
        return self.by, self.value

    # TODO: método que convierta selectores css en xpath (si el selector css devuelve múltiples, el xpath debe devolver
    #  los mismo). Para que funcione el concatenate con diferentes tipos

    def get_descendant(self, other : "BSLocator") -> "BSLocator":
        if self.by is By.XPATH:
            return BSLocator.xpath(f"{self.value}{other.value}")

        if self.by is By.CSS_SELECTOR:
            subselectors: list[str] = [s.strip() for s in self.value.split(',')]
            return BSLocator.css(", ".join([
                f"{ss} {other.value}" for ss in subselectors if ss
            ]))
        raise Exception("BSLocator Concatenation Error")

    def get_nth_element(self, i : int) -> "BSLocator":
        if self.by is By.XPATH:
            return BSLocator.xpath(f"({self.value})[{i}]")
        if self.by is By.CSS_SELECTOR:
            return BSLocator.css(", ".join([
                ss.strip() + f":nth-child({i})"
                for ss in self.value.split(',')
                if ss.strip()
            ]))

            #return BSLocator.css(f'{self.value}:nth-child({i})')
        raise Exception(f"Error getting {i}-th child of {self.value}")

    @staticmethod
    def id(element_id: str) -> "BSLocator":
        """Create a locator by ID."""
        return BSLocator(By.ID, element_id)

    @staticmethod
    def name(name: str) -> "BSLocator":
        """Create a locator by name attribute."""
        return BSLocator(By.NAME, name)

    @staticmethod
    def class_name(class_name: str) -> "BSLocator":
        """Create a locator by class name."""
        return BSLocator(By.CLASS_NAME, class_name)

    @staticmethod
    def tag_name(tag_name: str) -> "BSLocator":
        """Create a locator by tag name."""
        return BSLocator(By.TAG_NAME, tag_name)

    @staticmethod
    def css(css_selector: str) -> "BSLocator":
        """Create a locator by CSS selector."""
        return BSLocator(By.CSS_SELECTOR, css_selector)

    @staticmethod
    def xpath(xpath: str) -> "BSLocator":
        """Create a locator by XPath."""
        return BSLocator(By.XPATH, xpath)

    @staticmethod
    def link_text(text: str) -> "BSLocator":
        """Create a locator by exact link text."""
        return BSLocator(By.LINK_TEXT, text)

    @staticmethod
    def partial_link_text(text: str) -> "BSLocator":
        """Create a locator by partial link text."""
        return BSLocator(By.PARTIAL_LINK_TEXT, text)