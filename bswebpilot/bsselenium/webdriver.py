import platform
import random
import subprocess
import sys
import time

import undetected_chromedriver as uc  # TODO: mirar v2 https://pypi.org/project/undetected-chromedriver/2.1.1/
from selenium.common import TimeoutException, ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import cast
from typing_extensions import override
from webdriver_manager.chrome import ChromeDriverManager

from ..base import BSWebPilotSync
from bswebpilot.utils.locator import BSLocator


# TODO: implementar métodos faltantes y usar timeout

class BSWebDriverSync(BSWebPilotSync):
    driver: uc.Chrome | None = None
    options: uc.ChromeOptions | None = None

    # Settings
    medium_waiting_time: float = 15.0  # para esperas explícitas
    short_waiting_time: float = 2.0  # para búsqueda de elementos
    min_human_typing_wait: float = 0.04
    max_human_typing_wait: float = 0.19

    def __init__(self, is_headless: bool = False, window_resolution: tuple[int, int] | None = None):
        super().__init__(is_headless, window_resolution)
        self._is_headless = is_headless
        self._window_resolution = window_resolution

    def __enter__(self) -> "BSWebDriverSync":
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.quit()

    def __del__(self) -> None:
        """Último recurso de limpieza. Usar quit() o el context manager explícitamente."""
        if self.driver is not None:
            try:
                self.driver.quit()
            except Exception:
                pass

    def _set_chromedriver_option(self, is_headless: bool = False) -> None:
        self.options = uc.ChromeOptions()
        self.options.add_argument("--incognito")
        if is_headless:
            self.options.add_argument("--headless")

    def _build_chromedriver(self, window_resolution: tuple[int, int] | None = None) -> None:
        self.driver = uc.Chrome(options=self.options, driver_executable_path=self._get_driver_path())
        self.driver.execute_cdp_cmd(
            "Network.setUserAgentOverride", {
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"}
        )
        if window_resolution:
            self.driver.set_window_size(*window_resolution)

    @override
    def initialize(self) -> None:
        """Inicializa las opciones de Chrome y construye el ChromeDriver."""
        self._set_chromedriver_option(self._is_headless)
        self._build_chromedriver(self._window_resolution)

    @override
    def quit(self):
        self.driver.quit()

    def close_tab(self, window_handle: str):
        original_handle: str = self.driver.current_window_handle
        self.driver.switch_to.window(window_handle)
        self.driver.close()
        if original_handle != window_handle and original_handle in self.driver.window_handles:
            self.driver.switch_to.window(original_handle)

    def set_implicit_wait(self, wait_time: float) -> None:
        self.driver.implicitly_wait(wait_time)

    @override
    def navigate_to(self, url: str) -> None:
        self.driver.get(url)

    @override
    def maximize_window(self) -> None:
        self.driver.maximize_window()

    def grab_focus(self) -> None:
        self.driver.execute_script("window.focus();")

    # Elements
    # TODO: implementar timeout
    def find_element(self, locator: BSLocator) -> WebElement:
        return self.driver.find_element(locator.by, locator.value)

    # TODO: implementar timeout
    def find_elements(self, locator: BSLocator) -> list[WebElement]:
        return self.driver.find_elements(locator.by, locator.value)

    @override
    def get_elements_count(self, locator: BSLocator, timeout: float = 10) -> int:
        return len(self.find_elements(locator))

    @override
    def click(self, locator: BSLocator, timeout: float = 10) -> None:
        self.wait_element_to_be_clickable(locator)
        self.find_element(locator).click()

    @override
    def click_js(self, locator: BSLocator) -> None:
        self.wait_element_to_be_clickable(locator)
        self.driver.execute_script("arguments[0].click();", self.find_element(locator))

    @override
    def click_nth(self, locator: BSLocator, index: int, timeout: float = 10) -> None:
        self.find_elements(locator)[index].click()

    @override
    def manual_click_element(self, locator: BSLocator, timeout: float = 10) -> None:
        raise NotImplementedError

    @override
    def clear(self, locator: BSLocator):
        self.wait_element_to_be_clickable(locator)
        self.find_element(locator).clear()

    def send_keys(self, locator: BSLocator, content: str):
        self.wait_element_to_be_present(locator)
        self.find_element(locator).send_keys(content)

    def clear_and_send_keys(self, locator: BSLocator, content: str):
        self.clear(locator)
        self.send_keys(locator, content)

    @override
    def clear_and_human_type(self, locator: BSLocator, content: str):
        self.wait_random(self.min_human_typing_wait, self.max_human_typing_wait)
        self.clear(locator)
        self.wait_random(self.min_human_typing_wait, self.max_human_typing_wait)
        self.human_type(locator, content)

    @override
    def human_type(self, locator: BSLocator, content: str):
        self.wait_element_to_be_clickable(locator)
        elem = self.find_element(locator)
        time.sleep(random.uniform(self.min_human_typing_wait, self.max_human_typing_wait))
        for char in str(content):
            elem.send_keys(char)
            time.sleep(random.uniform(self.min_human_typing_wait, self.max_human_typing_wait))

    @override
    def get_element_text(self, locator: BSLocator, unsafe_mode: bool = True, timeout=10) -> str | None:
        self.wait_element_to_be_visible(locator, timeout, unsafe_mode)
        try:
            return self.find_element(locator).text
        except TimeoutException as e:
            if unsafe_mode: raise e

    @override
    def get_elements_text(self, locator: BSLocator, timeout: float = 10) -> list[str]:
        raise NotImplementedError

    @override
    def get_attribute_value(self, locator: BSLocator, attribute: str) -> str:
        self.wait_element_to_be_present(locator)
        return self.find_element(locator).get_attribute(attribute).strip()

    # Presence of elements
    @override
    def is_element_present(self, locator: BSLocator, timeout: float = 10):
        try:
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(locator.as_tuple()))
            return True
        except TimeoutException:
            return False

    @override
    def is_element_not_present(self, locator: BSLocator, timeout: float = 10) -> bool:
        return not self.is_element_present(locator, timeout)

    @override
    def is_element_visible(self, locator: BSLocator, timeout: float = 10, tolerance_time: float | None = None):
        t = tolerance_time if tolerance_time is not None else timeout
        return self.is_element_present(locator, t) and self.find_element(locator).is_displayed()

    def is_element_clickable(self, locator: BSLocator, timeout: float = 10, tolerance_time: float | None = None):
        t = tolerance_time if tolerance_time is not None else timeout
        try:
            WebDriverWait(self.driver, t).until(EC.element_to_be_clickable(locator.as_tuple()))
            return True
        except TimeoutException:
            return False
        except ElementClickInterceptedException:
            return False

    # Explicit waits
    # TODO: añadir opción para generar o no excepción
    @override
    def wait_element_to_be_present(self, locator: BSLocator, timeout: float = 10):
        WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(locator.as_tuple()))

    def wait_element_to_be_clickable(self, locator: BSLocator, timeout: float = 10,
                                     raise_exception: bool = True):
        try:
            WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(locator.as_tuple()))
        except TimeoutException as e:
            if raise_exception:
                raise e

    def wait_element_to_be_visible(self, locator: BSLocator, timeout: float = 10, raise_exception: bool = True):
        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(locator.as_tuple()))
        except TimeoutException as e:
            if raise_exception:
                raise e
                # TODO: replicar esto en todos los waits que lanzan excepción.

    def wait_element_to_be_invisible(self, locator: BSLocator, timeout: float = 10,
                                     raise_exception: bool = False):
        try:
            WebDriverWait(self.driver, timeout).until(EC.invisibility_of_element_located(locator.as_tuple()))
        except TimeoutException as e:
            if raise_exception: raise e

    def wait_page_to_be_loaded(self, max_time: float = 10):
        WebDriverWait(self.driver, max_time).until(
            lambda d: d.execute_script("return document.readyState") == "complete")

    def wait_element_class_to_contain(self, locator: BSLocator, content: str, max_time: float = 10):
        WebDriverWait(self.driver, max_time).until(
            lambda d: content in self.find_element(locator).get_attribute("class"))

    def wait_attribute_to_contain(self, locator: BSLocator, attr: str, content: str, tolerance_time: float = 10,
                                  raise_exception: bool = False):
        try:
            WebDriverWait(self.driver, tolerance_time).until(
                lambda d: content in self.find_element(locator).get_attribute(attr))
        except Exception as e:
            if raise_exception: raise e

    def wait_text_to_contain(self, locator: BSLocator, content: str, tolerance_time: float = 10,
                             raise_exception: bool = False):
        try:
            WebDriverWait(self.driver, tolerance_time).until(lambda d: content in self.find_element(locator).text)
        except Exception as e:
            if raise_exception: raise e

    # Aux
    @override
    def get_current_url(self) -> str:
        return self.driver.current_url

    def scroll_element_into_view(self, element_locator: BSLocator, timeout: float = 10) -> None:
        # TODO: no estamos haciendo nada con el timeout
        element: WebElement = self.find_element(element_locator)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)

    def scroll_to_page_top(self) -> None:
        self.execute_script("window.scrollTo(0, 0);")

    def get_class(self, locator: BSLocator) -> str:
        """Devuelve el valor del atributo 'class' del elemento localizado (cadena vacía si no lo tiene)."""
        self.wait_element_to_be_present(locator)
        return self.find_element(locator).get_attribute("class") or ""

    def execute_script(self, script: str) -> None:
        self.driver.execute_script(script)

    _VALID_BY_VALUES: frozenset[str] = frozenset({
        By.ID, By.XPATH, By.CSS_SELECTOR, By.CLASS_NAME,
        By.TAG_NAME, By.NAME, By.LINK_TEXT, By.PARTIAL_LINK_TEXT,
    })

    @staticmethod
    def _locator_to_by(locator: BSLocator) -> By:
        """
        Extrae el valor By de Selenium a partir de un BSLocator.
        BSLocator.by ya almacena directamente las constantes de By (By.ID, By.XPATH, etc.),
        por lo que este método sirve como punto de conversión explícita y como puente
        para cuando BSLocator migre a su propio enum interno.
        """
        if locator.by not in BSWebDriverSync._VALID_BY_VALUES:
            raise ValueError(f"Tipo de locator no soportado: {locator.by!r}")
        return cast(By, cast(object, locator.by))

    def switch_to_frame(self, iframe_locator: BSLocator) -> None:
        WebDriverWait(self.driver, 10).until(
            EC.frame_to_be_available_and_switch_to_it(iframe_locator.as_tuple())
        )

    def switch_to_nested_frame(self, *iframe_locators: BSLocator) -> None:
        """Navega a través de iframes anidados en el orden indicado."""
        for locator in iframe_locators:
            WebDriverWait(self.driver, 10).until(
                EC.frame_to_be_available_and_switch_to_it(locator.as_tuple())
            )

    def switch_to_default_content(self) -> None:
        self.driver.switch_to.default_content()

    @override
    def save_screenshot(self, file_path: str = "screenshot.png"):
        self.driver.save_screenshot(file_path)

    def save_element_screenshot(self, element_locator: BSLocator, file_path: str = "screenshot.png"):
        self.find_element(element_locator).screenshot(file_path)

    @staticmethod
    def _codesign_if_macos(path: str) -> None:
        """
        En macOS, elimina atributos extendidos (como com.apple.provenance)
        y aplica una firma ad-hoc al binario indicado para que Gatekeeper
        permita su ejecución sin intervención del usuario.
        """
        if sys.platform != "darwin":
            return
        try:
            # Eliminar atributos extendidos que provocan SIGKILL (-9)
            subprocess.run(
                ["xattr", "-cr", path],
                check=False,
                capture_output=True,
            )
            subprocess.run(
                ["codesign", "--force", "--deep", "--sign", "-", path],
                check=True,
                capture_output=True,
            )
        except Exception:
            pass  # Si falla (ej. ya firmado y válido), ignorar

    @staticmethod
    def _get_driver_path() -> str:
        """
        Descarga el chromedriver adecuado para la arquitectura actual.
        En Apple Silicon (arm64) fuerza la descarga del binario mac-arm64
        para evitar que webdriver-manager descargue el binario x86_64
        que macOS mata con SIGKILL (-9).
        Tras la descarga, aplica firma ad-hoc para que Gatekeeper lo permita.
        """
        machine = platform.machine().lower()
        if machine == "arm64":
            from webdriver_manager.core.os_manager import OperationSystemManager
            manager = ChromeDriverManager(os_system_manager=OperationSystemManager(os_type="mac-arm64"))
        else:
            manager = ChromeDriverManager()
        path = manager.install()
        BSWebDriverSync._codesign_if_macos(path)
        return path
