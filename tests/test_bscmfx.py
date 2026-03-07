"""
Tests para BSCmfx (Camoufox/Playwright wrapper).

Estructura:
  - TestBSCmfxUnit         → tests unitarios puros, sin navegador
  - TestBSCmfxInit         → tests de inicialización y ciclo de vida
  - TestBSCmfxNavigation   → tests de navegación
  - TestBSCmfxElements     → tests de verificación e interacción con elementos
  - TestBSCmfxScreenshot   → tests de captura de pantalla

URL base: https://example.com  (página estable, minimalista, sin JS complejo)
"""
import os
import pytest
import pytest_asyncio
from selenium.webdriver.common.by import By

from bswebpilot.bsplaywright.bscmfx import BSCmfx
from bswebpilot.utils.locator import BSLocator

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

TEST_URL = "https://example.com"

# Locators sobre example.com
LOC_H1 = BSLocator.css("h1")
LOC_PARAGRAPHS = BSLocator.css("p")
LOC_LINK = BSLocator.css("a")
LOC_MISSING = BSLocator.css("#elemento-que-no-existe-xyz-999")
LOC_H1_XPATH = BSLocator.xpath("//h1")


# ===========================================================================
# Tests unitarios — no necesitan navegador
# ===========================================================================

class TestBSCmfxUnit:
    """Pruebas unitarias puras de métodos estáticos / sin navegador."""

    # --- get_pw_locator ---

    def test_get_pw_locator_css(self):
        """Un selector CSS se devuelve tal cual."""
        loc = BSLocator.css("#mi-id > span.clase")
        assert BSCmfx._get_pw_locator(loc) == "#mi-id > span.clase"

    def test_get_pw_locator_xpath(self):
        """Un XPath se devuelve con el prefijo 'xpath='."""
        loc = BSLocator.xpath('//div[@id="contenedor"]')
        assert BSCmfx._get_pw_locator(loc) == 'xpath=//div[@id="contenedor"]'

    def test_get_pw_locator_invalid_raises_value_error(self):
        """Un tipo de locator no soportado (p. ej. 'id') debe lanzar ValueError."""
        loc = BSLocator(By.ID, "mi-id")
        with pytest.raises(ValueError):
            BSCmfx._get_pw_locator(loc)

    # --- _get_locale ---

    def test_get_locale_returns_string(self):
        """_get_locale() debe devolver un string no vacío."""
        locale_str = BSCmfx._get_locale()
        assert isinstance(locale_str, str)
        assert len(locale_str) > 0

    # --- _get_screen_resolution ---

    def test_get_screen_resolution_default(self):
        """_get_screen_resolution() devuelve una tupla de dos enteros positivos."""
        res = BSCmfx._get_screen_resolution()
        assert isinstance(res, tuple)
        assert len(res) == 2
        assert all(isinstance(v, int) and v > 0 for v in res)

    # --- _get_platform_and_web_gl ---

    def test_get_platform_and_web_gl_returns_valid_os(self):
        """_get_platform_and_web_gl() devuelve un OS reconocido por Camoufox."""
        os_name, webgl = BSCmfx._get_platform_and_web_gl()
        assert os_name in ("windows", "macos", "linux")
        assert isinstance(webgl, tuple)
        assert len(webgl) == 2


# ===========================================================================
# Tests de inicialización y ciclo de vida
# ===========================================================================

class TestBSCmfxInit:
    """Pruebas sobre arranque, parada y context manager."""

    @pytest.mark.asyncio
    async def test_initialize_sets_browser_and_page(self):
        """initialize() debe dejar browser y page distintos de None."""
        cmfx = BSCmfx(is_headless=True, humanize=False)
        await cmfx.initialize()
        try:
            assert cmfx.browser is not None
            assert cmfx.page is not None
        finally:
            await cmfx.quit()

    @pytest.mark.asyncio
    async def test_quit_clears_resources(self):
        """quit() debe poner a None browser, page y _camoufox_instance."""
        cmfx = BSCmfx(is_headless=True, humanize=False)
        await cmfx.initialize()
        await cmfx.quit()
        assert cmfx.browser is None
        assert cmfx.page is None
        assert cmfx._camoufox_instance is None

    @pytest.mark.asyncio
    async def test_context_manager_enters_and_exits(self):
        """El context manager async with debe inicializar y cerrar correctamente."""
        async with BSCmfx(is_headless=True, humanize=False) as cmfx:
            assert cmfx.browser is not None
            assert cmfx.page is not None
        # Tras salir del bloque los recursos deben estar liberados
        assert cmfx.browser is None
        assert cmfx.page is None

    @pytest.mark.asyncio
    async def test_initialize_is_idempotent_after_quit(self):
        """Se puede volver a llamar a initialize() tras quit() sin errores."""
        cmfx = BSCmfx(is_headless=True, humanize=False)
        await cmfx.initialize()
        await cmfx.quit()
        await cmfx.initialize()
        assert cmfx.browser is not None
        await cmfx.quit()


# ===========================================================================
# Tests de navegación
# ===========================================================================

class TestBSCmfxNavigation:
    """Pruebas de navegación (requieren navegador)."""

    @pytest.mark.asyncio
    async def test_navigate_to_changes_url(self, browser: BSCmfx):
        """navigate_to() debe cambiar la URL actual a la destino."""
        await browser.navigate_to(TEST_URL)
        current = await browser.get_current_url()
        assert TEST_URL in current

    @pytest.mark.asyncio
    async def test_get_current_url_returns_string(self, browser: BSCmfx):
        """get_current_url() debe devolver un string que empiece por 'http'."""
        await browser.navigate_to(TEST_URL)
        url = await browser.get_current_url()
        assert isinstance(url, str)
        assert url.startswith("http")

    @pytest.mark.asyncio
    async def test_wait_page_to_be_loaded_does_not_raise(self, browser: BSCmfx):
        """wait_page_to_be_loaded() no debe lanzar excepción tras navegar."""
        await browser.navigate_to(TEST_URL)
        await browser.wait_page_to_be_loaded(timeout=30)
        url = await browser.get_current_url()
        assert url is not None and len(url) > 0

    @pytest.mark.asyncio
    async def test_navigate_multiple_times(self, browser: BSCmfx):
        """Navegar varias veces seguidas no debe provocar errores."""
        for _ in range(3):
            await browser.navigate_to(TEST_URL)
        url = await browser.get_current_url()
        assert TEST_URL in url


# ===========================================================================
# Tests de verificación de elementos
# ===========================================================================

class TestBSCmfxElements:
    """Pruebas sobre detección, conteo y lectura de elementos."""

    @pytest.mark.asyncio
    async def test_is_element_present_true(self, browser: BSCmfx):
        """is_element_present() → True para un elemento que existe en el DOM."""
        await browser.navigate_to(TEST_URL)
        result = await browser.is_element_present(LOC_H1, timeout=10)
        assert result is True

    @pytest.mark.asyncio
    async def test_is_element_present_false(self, browser: BSCmfx):
        """is_element_present() → False para un elemento que NO existe."""
        await browser.navigate_to(TEST_URL)
        result = await browser.is_element_present(LOC_MISSING, timeout=3)
        assert result is False

    @pytest.mark.asyncio
    async def test_is_element_not_present(self, browser: BSCmfx):
        """is_element_not_present() → True para un elemento inexistente."""
        await browser.navigate_to(TEST_URL)
        result = await browser.is_element_not_present(LOC_MISSING, timeout=5)
        assert result is True

    @pytest.mark.asyncio
    async def test_is_element_visible_true(self, browser: BSCmfx):
        """is_element_visible() → True para el <h1> de example.com."""
        await browser.navigate_to(TEST_URL)
        result = await browser.is_element_visible(LOC_H1, timeout=10)
        assert result is True

    @pytest.mark.asyncio
    async def test_is_element_visible_false(self, browser: BSCmfx):
        """is_element_visible() → False para un elemento inexistente."""
        await browser.navigate_to(TEST_URL)
        result = await browser.is_element_visible(LOC_MISSING, timeout=3)
        assert result is False

    @pytest.mark.asyncio
    async def test_get_element_text_h1(self, browser: BSCmfx):
        """get_element_text() debe devolver el texto del <h1>."""
        await browser.navigate_to(TEST_URL)
        text = await browser.get_element_text(LOC_H1, timeout=10)
        assert isinstance(text, str)
        assert len(text) > 0

    @pytest.mark.asyncio
    async def test_get_element_text_xpath(self, browser: BSCmfx):
        """get_element_text() funciona también con locators XPath."""
        await browser.navigate_to(TEST_URL)
        text = await browser.get_element_text(LOC_H1_XPATH, timeout=10)
        assert isinstance(text, str)
        assert len(text) > 0

    @pytest.mark.asyncio
    async def test_get_element_text_missing_no_raise(self, browser: BSCmfx):
        """get_element_text() con raise_exception=False devuelve None si no existe."""
        await browser.navigate_to(TEST_URL)
        result = await browser.get_element_text(LOC_MISSING, timeout=3, raise_exception=False)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_elements_count_paragraphs(self, browser: BSCmfx):
        """get_elements_count() debe devolver > 0 para los <p> de example.com."""
        await browser.navigate_to(TEST_URL)
        count = await browser.get_elements_count(LOC_PARAGRAPHS, timeout=10)
        assert isinstance(count, int)
        assert count > 0

    @pytest.mark.asyncio
    async def test_get_elements_count_missing(self, browser: BSCmfx):
        """get_elements_count() devuelve 0 para un selector que no existe."""
        await browser.navigate_to(TEST_URL)
        count = await browser.get_elements_count(LOC_MISSING, timeout=3)
        assert count == 0

    @pytest.mark.asyncio
    async def test_get_elements_text_paragraphs(self, browser: BSCmfx):
        """get_elements_text() devuelve una lista de strings para los <p>."""
        await browser.navigate_to(TEST_URL)
        texts = await browser.get_elements_text(LOC_PARAGRAPHS, timeout=10)
        assert isinstance(texts, list)
        assert len(texts) > 0
        assert all(isinstance(t, str) for t in texts)

    @pytest.mark.asyncio
    async def test_get_elements_text_missing_returns_empty(self, browser: BSCmfx):
        """get_elements_text() devuelve lista vacía si no hay elementos."""
        await browser.navigate_to(TEST_URL)
        texts = await browser.get_elements_text(LOC_MISSING, timeout=3)
        assert texts == []

    @pytest.mark.asyncio
    async def test_get_attribute_value(self, browser: BSCmfx):
        """get_attribute_value() devuelve el href del enlace de example.com."""
        await browser.navigate_to(TEST_URL)
        href = await browser.get_attribute_value(LOC_LINK, "href", timeout=10)
        assert href is not None
        assert href.startswith("http")

    @pytest.mark.asyncio
    async def test_check_attribute_is_equals_case_insensitive(self, browser: BSCmfx):
        """check_attribute_is_equals() con ignore_case=True funciona correctamente."""
        await browser.navigate_to(TEST_URL)
        href = await browser.get_attribute_value(LOC_LINK, "href", timeout=10)
        result = await browser.check_attribute_is_equals(
            LOC_LINK, "href", href.upper(), ignore_case=True
        )
        assert result is True

    @pytest.mark.asyncio
    async def test_wait_element_to_be_present_does_not_raise(self, browser: BSCmfx):
        """wait_element_to_be_present() no lanza excepción para un elemento existente."""
        await browser.navigate_to(TEST_URL)
        await browser.wait_element_to_be_present(LOC_H1, timeout=10)

    @pytest.mark.asyncio
    async def test_wait_element_to_be_visible_does_not_raise(self, browser: BSCmfx):
        """wait_element_to_be_visible() no lanza excepción para un elemento visible."""
        await browser.navigate_to(TEST_URL)
        await browser.wait_element_to_be_visible(LOC_H1, timeout=10)


# ===========================================================================
# Tests de captura de pantalla
# ===========================================================================

class TestBSCmfxScreenshot:
    """Pruebas de save_screenshot()."""

    @pytest.mark.asyncio
    async def test_save_screenshot_creates_file(self, browser: BSCmfx, tmp_path):
        """save_screenshot() debe crear un fichero PNG no vacío."""
        await browser.navigate_to(TEST_URL)
        path = str(tmp_path / "captura.png")
        await browser.save_screenshot(path)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0

    @pytest.mark.asyncio
    async def test_save_screenshot_after_navigation(self, browser: BSCmfx, tmp_path):
        """La captura tras navegar refleja la página cargada (fichero no vacío)."""
        await browser.navigate_to(TEST_URL)
        await browser.wait_page_to_be_loaded(timeout=15)
        path = str(tmp_path / "captura_cargada.png")
        await browser.save_screenshot(path)
        assert os.path.getsize(path) > 5000  # al menos 5 KB → página real

