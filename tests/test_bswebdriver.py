"""
Tests para BSWebDriver (undetected-chromedriver/Selenium wrapper).

Estructura:
  - TestBSWebDriverUnit        → tests unitarios puros, sin navegador
  - TestBSWebDriverInit        → tests de inicialización y ciclo de vida
  - TestBSWebDriverNavigation  → tests de navegación
  - TestBSWebDriverElements    → tests de verificación e interacción con elementos
  - TestBSWebDriverScreenshot  → tests de captura de pantalla

URL base: https://example.com  (página estable, minimalista, sin JS complejo)
"""
import os
import pytest

from bswebpilot.bsselenium.webdriver import BSWebDriver
from bswebpilot.utils.locator import BSLocator

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

TEST_URL = "https://example.com"

# Locators sobre example.com
LOC_H1           = BSLocator.css("h1")
LOC_PARAGRAPHS   = BSLocator.css("p")
LOC_LINK         = BSLocator.css("a")
LOC_MISSING      = BSLocator.css("#elemento-que-no-existe-xyz-999")
LOC_H1_XPATH     = BSLocator.xpath("//h1")

# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------

@pytest.fixture(scope="function")
def driver():
    """
    Inicializa BSWebDriver en modo headless antes de cada test
    y lo cierra automáticamente al terminar.
    """
    wd = BSWebDriver(is_headless=True)
    yield wd
    wd.quit()


# ===========================================================================
# Tests unitarios — no necesitan navegador
# ===========================================================================

class TestBSWebDriverUnit:
    """Pruebas unitarias puras de métodos estáticos / sin navegador."""

    def test_wait_random_does_not_raise(self):
        """wait_random() no debe lanzar excepción con valores válidos."""
        BSWebDriver.wait_random(0.01, 0.05)

    def test_wait_static_does_not_raise(self):
        """wait_static() no debe lanzar excepción con un tiempo pequeño."""
        BSWebDriver.wait_static(0.01)

    def test_locator_css_as_tuple(self):
        """BSLocator.css() devuelve el by y value correctos."""
        loc = BSLocator.css("h1")
        by, value = loc.as_tuple()
        assert value == "h1"

    def test_locator_xpath_as_tuple(self):
        """BSLocator.xpath() devuelve el by y value correctos."""
        loc = BSLocator.xpath("//h1")
        by, value = loc.as_tuple()
        assert value == "//h1"


# ===========================================================================
# Tests de inicialización y ciclo de vida
# ===========================================================================

class TestBSWebDriverInit:
    """Pruebas sobre arranque y parada del driver."""

    def test_driver_starts_and_quits(self):
        """BSWebDriver arranca correctamente y se cierra sin errores."""
        wd = BSWebDriver(is_headless=True)
        assert wd.driver is not None
        wd.quit()

    def test_driver_is_headless_by_default_param(self):
        """El driver creado con is_headless=True expone un objeto driver válido."""
        wd = BSWebDriver(is_headless=True)
        try:
            assert wd.driver is not None
        finally:
            wd.quit()

    def test_default_waiting_times(self):
        """Los tiempos de espera por defecto deben tener valores razonables."""
        wd = BSWebDriver(is_headless=True)
        try:
            assert wd.medium_waiting_time > 0
            assert wd.short_waiting_time > 0
            assert wd.min_human_typing_wait > 0
            assert wd.max_human_typing_wait > wd.min_human_typing_wait
        finally:
            wd.quit()


# ===========================================================================
# Tests de navegación
# ===========================================================================

class TestBSWebDriverNavigation:
    """Pruebas de navegación (requieren navegador)."""

    def test_navigate_to_changes_url(self, driver: BSWebDriver):
        """navigate_to() debe cambiar la URL actual a la destino."""
        driver.navigate_to(TEST_URL)
        assert TEST_URL in driver.get_current_url()

    def test_get_current_url_returns_string(self, driver: BSWebDriver):
        """get_current_url() debe devolver un string que empiece por 'http'."""
        driver.navigate_to(TEST_URL)
        url = driver.get_current_url()
        assert isinstance(url, str)
        assert url.startswith("http")

    def test_wait_page_to_be_loaded_does_not_raise(self, driver: BSWebDriver):
        """wait_page_to_be_loaded() no debe lanzar excepción tras navegar."""
        driver.navigate_to(TEST_URL)
        driver.wait_page_to_be_loaded(max_time=30)
        assert driver.get_current_url() is not None

    def test_navigate_multiple_times(self, driver: BSWebDriver):
        """Navegar varias veces seguidas no debe provocar errores."""
        for _ in range(3):
            driver.navigate_to(TEST_URL)
        assert TEST_URL in driver.get_current_url()

    def test_maximize_window_does_not_raise(self, driver: BSWebDriver):
        """maximize_window() no debe lanzar excepción."""
        driver.navigate_to(TEST_URL)
        driver.maximize_window()


# ===========================================================================
# Tests de verificación de elementos
# ===========================================================================

class TestBSWebDriverElements:
    """Pruebas sobre detección, lectura y atributos de elementos."""

    def test_is_element_present_true(self, driver: BSWebDriver):
        """is_element_present() → True para un elemento que existe en el DOM."""
        driver.navigate_to(TEST_URL)
        assert driver.is_element_present(LOC_H1, timeout=10) is True

    def test_is_element_present_false(self, driver: BSWebDriver):
        """is_element_present() → False para un elemento que NO existe."""
        driver.navigate_to(TEST_URL)
        assert driver.is_element_present(LOC_MISSING, timeout=3) is False

    def test_is_element_displayed_true(self, driver: BSWebDriver):
        """is_element_displayed() → True para el <h1> de example.com."""
        driver.navigate_to(TEST_URL)
        assert driver.is_element_displayed(LOC_H1, tolerance_time=10) is True

    def test_is_element_displayed_false(self, driver: BSWebDriver):
        """is_element_displayed() → False para un elemento que NO existe."""
        driver.navigate_to(TEST_URL)
        assert driver.is_element_displayed(LOC_MISSING, tolerance_time=3) is False

    def test_is_element_clickable_true(self, driver: BSWebDriver):
        """is_element_clickable() → True para el enlace de example.com."""
        driver.navigate_to(TEST_URL)
        assert driver.is_element_clickable(LOC_LINK, tolerance_time=10) is True

    def test_find_element_returns_element(self, driver: BSWebDriver):
        """find_element() devuelve un WebElement válido para el <h1>."""
        driver.navigate_to(TEST_URL)
        driver.wait_element_to_be_present(LOC_H1)
        elem = driver.find_element(LOC_H1)
        assert elem is not None

    def test_find_elements_returns_list(self, driver: BSWebDriver):
        """find_elements() devuelve una lista no vacía para los <p>."""
        driver.navigate_to(TEST_URL)
        driver.wait_element_to_be_present(LOC_PARAGRAPHS)
        elements = driver.find_elements(LOC_PARAGRAPHS)
        assert isinstance(elements, list)
        assert len(elements) > 0

    def test_get_text_h1(self, driver: BSWebDriver):
        """get_text() devuelve el texto del <h1> de example.com."""
        driver.navigate_to(TEST_URL)
        text = driver.get_element_text(LOC_H1)
        assert isinstance(text, str)
        assert len(text) > 0

    def test_get_text_xpath(self, driver: BSWebDriver):
        """get_text() funciona también con locators XPath."""
        driver.navigate_to(TEST_URL)
        text = driver.get_element_text(LOC_H1_XPATH)
        assert isinstance(text, str)
        assert len(text) > 0

    def test_get_class_returns_string(self, driver: BSWebDriver):
        """get_class() devuelve un string (puede estar vacío en example.com)."""
        driver.navigate_to(TEST_URL)
        driver.wait_element_to_be_present(LOC_H1)
        cls = driver.get_class(LOC_H1)
        assert isinstance(cls, str)

    def test_get_attribute_href_link(self, driver: BSWebDriver):
        """El atributo href del enlace de example.com comienza por 'http'."""
        driver.navigate_to(TEST_URL)
        driver.wait_element_to_be_present(LOC_LINK)
        elem = driver.find_element(LOC_LINK)
        href = elem.get_attribute("href")
        assert href is not None
        assert href.startswith("http")

    def test_wait_element_to_be_present_does_not_raise(self, driver: BSWebDriver):
        """wait_element_to_be_present() no lanza excepción para un elemento existente."""
        driver.navigate_to(TEST_URL)
        driver.wait_element_to_be_present(LOC_H1)

    def test_wait_element_to_be_clickable_does_not_raise(self, driver: BSWebDriver):
        """wait_element_to_be_clickable() no lanza excepción para el enlace."""
        driver.navigate_to(TEST_URL)
        driver.wait_element_to_be_clickable(LOC_LINK)

    def test_wait_element_to_be_visible_does_not_raise(self, driver: BSWebDriver):
        """wait_element_to_be_visible() no lanza excepción para el <h1>."""
        driver.navigate_to(TEST_URL)
        driver.wait_element_to_be_visible(LOC_H1)

    def test_scroll_element_into_view_does_not_raise(self, driver: BSWebDriver):
        """scroll_element_into_view() no debe lanzar excepción."""
        driver.navigate_to(TEST_URL)
        driver.wait_element_to_be_present(LOC_LINK)
        driver.scroll_element_into_view(LOC_LINK)

    def test_execute_script_returns_no_error(self, driver: BSWebDriver):
        """execute_script() no lanza excepción con un script válido."""
        driver.navigate_to(TEST_URL)
        driver.execute_script("document.title = 'test';")


# ===========================================================================
# Tests de captura de pantalla
# ===========================================================================

class TestBSWebDriverScreenshot:
    """Pruebas de save_screenshot() y save_element_screenshot()."""

    def test_save_screenshot_creates_file(self, driver: BSWebDriver, tmp_path):
        """save_screenshot() debe crear un fichero PNG no vacío."""
        driver.navigate_to(TEST_URL)
        path = str(tmp_path / "captura.png")
        driver.save_screenshot(path)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0

    def test_save_screenshot_after_navigation(self, driver: BSWebDriver, tmp_path):
        """La captura tras navegar refleja la página cargada (fichero > 5 KB)."""
        driver.navigate_to(TEST_URL)
        driver.wait_page_to_be_loaded(max_time=15)
        path = str(tmp_path / "captura_cargada.png")
        driver.save_screenshot(path)
        assert os.path.getsize(path) > 5000

    def test_save_element_screenshot_creates_file(self, driver: BSWebDriver, tmp_path):
        """save_element_screenshot() crea un PNG del elemento indicado."""
        driver.navigate_to(TEST_URL)
        driver.wait_element_to_be_visible(LOC_H1)
        path = str(tmp_path / "elemento.png")
        driver.save_element_screenshot(LOC_H1, path)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0


# ===========================================================================
# Tests manuales / visuales — navegador visible
# ===========================================================================

#VISIBLE_TEST_URL = TEST_URL  # cambia esta constante para probar otra URL
VISIBLE_TEST_URL = "https://casinia-3529.com/es/sport"  # cambia esta constante para probar otra URL


@pytest.mark.manual
class TestBSWebDriverVisible:
    """
    Tests que arrancan el navegador en modo VISIBLE (no headless).
    Se excluyen de la suite automática; para ejecutarlos manualmente:

        pytest -m manual tests/test_bswebdriver.py::TestBSWebDriverVisible
    """

    def test_visible_navigate_to_url(self):
        """Arranca Chrome visible, navega a VISIBLE_TEST_URL y verifica la URL."""
        wd = BSWebDriver(is_headless=False)
        try:
            wd.navigate_to(VISIBLE_TEST_URL)
            wd.wait_page_to_be_loaded(max_time=30)
            current_url = wd.get_current_url()
            assert isinstance(current_url, str)
            assert current_url.startswith("http")
            assert VISIBLE_TEST_URL in current_url
        finally:
            wd.quit()


