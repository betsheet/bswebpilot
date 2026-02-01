import platform
import locale
import re
import asyncio
import random
from tkinter import Tk
from typing import Any

from camoufox.async_api import AsyncCamoufox
from playwright.async_api import Browser, BrowserContext, Page, Locator, TimeoutError, expect
from bswebpilot.utils.locator import BSLocator


class BSCmfx:
    """
    Envoltorio asíncrono para Camoufox, el cual a su vez envuelve a Playwright.
    Diseñado para mantener una sesión de navegador activa de forma asíncrona.
    """
    _camoufox_instance: AsyncCamoufox | None = None
    browser: Browser | BrowserContext | None = None
    page: Page | None = None

    def __init__(self, is_headless: bool = False, humanize: bool = True, screen_resolution: tuple[int, int] | None = None,
                 **camoufox_config):
        """
        Constructor que almacena la configuración inicial.
        La inicialización real del navegador se hace en initialize().
        
        Args:
            is_headless (bool): Si es True, el navegador se ejecuta sin interfaz gráfica.
            humanize (bool): Si es True, humaniza las interacciones con el navegador.
            screen_resolution (tuple[int, int] | None): Resolución de pantalla (ancho, alto).
            Si es None, se detecta automáticamente.
            **camoufox_config: Argumentos adicionales de configuración para Camoufox.
        """
        self.is_headless = is_headless
        self.humanize = humanize
        self.screen_resolution = screen_resolution
        self.camoufox_config = camoufox_config

    async def initialize(self):
        """
        Inicializa la instancia de Camoufox, lanza el navegador y crea una nueva página.
        Este método debe ser llamado después de crear la instancia.
        """
        # Configuramos los parámetros principales para Camoufox
        os_and_web_gl_prop: tuple[str, tuple[str, str]] = self._get_platform_and_web_gl()
        config = {
            'headless': self.is_headless,
            'os': os_and_web_gl_prop[0],
            'webgl_config': os_and_web_gl_prop[1],
            'window': self.screen_resolution if self.screen_resolution is not None else self._get_screen_resolution(),
            'locale': self._get_locale(),
            'humanize': self.humanize,
            **self.camoufox_config
        }
        
        # Creamos la instancia de AsyncCamoufox
        self._camoufox_instance = AsyncCamoufox(**config)
        
        # Entramos en el contexto asíncrono para obtener el browser
        self.browser = await self._camoufox_instance.__aenter__()
        
        # Configuramos el viewport
        page_options = {}
        if config['window'] and len(config['window']) == 2:
            page_options['viewport'] = {
                'width': config['window'][0], 
                'height': config['window'][1]
            }
        
        # Creamos la página
        self.page = await self.browser.new_page(**page_options)
        
        return self

    # ========== Métodos auxiliares de configuración ==========
    
    @staticmethod
    def _get_locale() -> str:
        """Obtiene el locale del sistema."""
        return locale.getdefaultlocale()[0].replace('_', '-')

    @staticmethod
    def _get_screen_resolution() -> tuple[int, int]:
        """Obtiene la resolución de pantalla del sistema."""
        root: Tk = Tk()
        root.withdraw()
        to_return: tuple[int, int] = root.winfo_screenwidth(), root.winfo_screenheight()
        root.destroy()
        return to_return

    @staticmethod
    def _get_platform_and_web_gl() -> tuple[str, tuple[str, str]]:
        """Detecta el sistema operativo y configura WebGL apropiadamente."""
        os_name = platform.system()
        if os_name == "Windows":
            return 'windows', ('Google Inc. (NVIDIA)', 'ANGLE (NVIDIA, NVIDIA GeForce GTX 980 Direct3D11 vs_5_0 ps_5_0), or similar')
        elif os_name == "Darwin":
            return 'macos', ('Apple', 'Apple M1, or similar')
        elif os_name == "Linux":
            return 'linux', ('Intel', 'Intel(R) HD Graphics, or similar')
        raise Exception(f"Sistema operativo no válido detectado: {os_name}")

    @staticmethod
    def get_pw_locator(locator: BSLocator) -> str:
        """
        Convierte un BSLocator al formato de Playwright.
        
        Args:
            locator: BSLocator con tipo 'css selector' o 'xpath'
            
        Returns:
            String en formato de Playwright locator
        """
        if locator.by == 'css selector':
            return locator.value
        if locator.by == 'xpath':
            return f'xpath={locator.value}'
        raise ValueError(f'Tipo de selector no válido: {locator.by}')

    # ========== Métodos de navegación ==========
    
    async def navigate_to(self, url: str, timeout: float = 60):
        """
        Navega a la URL especificada.
        
        Args:
            url: URL a la que navegar
            timeout: Timeout en segundos (por defecto 60)
        """
        await self.page.goto(url, timeout=timeout*1000)

    async def save_screenshot(self, filepath: str):
        """Guarda una captura de pantalla en la ruta especificada."""
        await self.page.screenshot(path=filepath)

    # ========== Métodos de espera ==========
    
    @staticmethod
    async def wait_random(_min: float, _max: float) -> None:
        """Espera un tiempo aleatorio entre _min y _max segundos."""
        await asyncio.sleep(random.uniform(_min, _max))

    @staticmethod
    async def wait_static(wait_time: float) -> None:
        """Espera un tiempo fijo en segundos."""
        await asyncio.sleep(wait_time)

    async def wait_page_to_be_loaded(self, timeout: float = 10) -> None:
        """Espera a que la página esté completamente cargada."""
        await self.page.wait_for_load_state(timeout=timeout*1000)
        await self.wait_random(0.15, 0.3)

    # ========== Métodos de verificación de elementos ==========
    
    async def is_element_present(self, locator: BSLocator, timeout: float = 10) -> bool:
        """Verifica si un elemento está presente en el DOM."""
        try:
            await expect(self.page.locator(self.get_pw_locator(locator)).first).to_be_attached(timeout=timeout*1000)
            return True
        except AssertionError:
            return False

    async def is_element_visible(self, locator: BSLocator, timeout: float = 10) -> bool:
        """Verifica si un elemento es visible."""
        try:
            return await self.page.locator(self.get_pw_locator(locator)).first.is_visible(timeout=timeout*1000)
        except TimeoutError:
            return False

    async def wait_element_to_be_present(self, locator: BSLocator, timeout: float = 10) -> None:
        """Espera a que un elemento esté presente en el DOM."""
        await expect(self.page.locator(self.get_pw_locator(locator)).first).to_be_attached(timeout=timeout*1000)

    async def wait_element_to_be_visible(self, locator: BSLocator, timeout: float = 10):
        """Espera a que un elemento sea visible."""
        await expect(self.page.locator(self.get_pw_locator(locator)).first).to_be_visible(timeout=timeout*1000)

    async def wait_element_to_be_invisible(self, locator: BSLocator, timeout: float = 10):
        """Espera a que un elemento sea invisible."""
        await expect(self.page.locator(self.get_pw_locator(locator))).not_to_be_visible(timeout=timeout*1000)

    async def wait_element_to_be_enabled(self, locator: BSLocator, timeout: float = 10) -> None:
        """Espera a que un elemento esté habilitado."""
        await expect(self.page.locator(self.get_pw_locator(locator)).first).to_be_enabled(timeout=timeout*1000)

    async def wait_element_to_have_text(self, locator: BSLocator, text: str, timeout: float = 10) -> None:
        """Espera a que un elemento tenga un texto específico."""
        await expect(self.page.locator(self.get_pw_locator(locator))).to_have_text(text, timeout=timeout*1000)

    async def verify_attribute_contains(self, locator: BSLocator, attr: str, content: str, 
                                       ignore_case: bool = True, timeout: float = 10) -> None:
        """Verifica que un atributo de un elemento contenga cierto contenido."""
        await expect(self.page.locator(self.get_pw_locator(locator))).to_have_attribute(
            attr, re.compile(rf'.*{content}.*'), ignore_case=ignore_case, timeout=timeout*1000
        )

    async def check_attribute_is_equals(self, locator: BSLocator, attr: str, content: str, ignore_case: bool = False, timeout: float = 10) -> bool:
        attribute_value: str = await self.get_attribute_value(locator, attr, timeout)
        return attribute_value.lower() == content.lower() if ignore_case else attribute_value == content

    async def get_attribute_value(self, locator: BSLocator, attr: str, timeout: float = 10) -> str | None:
        return await self.page.locator(self.get_pw_locator(locator)).get_attribute(attr, timeout=timeout * 1000)

    # ========== Métodos de obtención de información ==========
    
    async def get_element_text(self, locator: BSLocator, timeout: float = 10, raise_exception: bool = True):
        """Obtiene el texto de un elemento."""
        try:
            return await self.page.locator(self.get_pw_locator(locator)).first.inner_text(timeout=timeout*1000)
        except TimeoutError as e:
            if raise_exception:
                raise e
            return None

    async def get_elements_text(self, locator: BSLocator, timeout: float = 10) -> list[str]:
        """Obtiene el texto de todos los elementos que coinciden con el locator."""
        try:
            await self.wait_element_to_be_present(locator, timeout)
            pw_locator: Locator = self.page.locator(self.get_pw_locator(locator))
            await expect(pw_locator.first).to_be_attached(timeout=timeout*1000)
        except AssertionError:
            return []
        return await pw_locator.all_inner_texts()

    async def get_elements_count(self, locator: BSLocator, timeout: float = 10) -> int:
        """Obtiene el número de elementos que coinciden con el locator."""
        pw_loc: Locator = self.page.locator(self.get_pw_locator(locator))
        try:
            await pw_loc.first.wait_for(state='attached', timeout=timeout * 1000)
            return await pw_loc.count()
        except TimeoutError:
            return 0

    # ========== Métodos de interacción con elementos ==========
    async def manual_click_element(self, locator: BSLocator, timeout: float = 10) -> None:
        locator: Locator = self.page.locator(self.get_pw_locator(locator))
        await locator.wait_for(state='visible', timeout=timeout * 1000)
        await locator.hover()
        await self.wait_random(0.1, 0.2)

        locator_box = await locator.first.bounding_box(timeout=timeout * 1000)
        await self.page.mouse.move(
            locator_box["x"] + locator_box["width"] / 2,
            locator_box["y"] + locator_box["height"] / 2
        )

        await self.page.mouse.down()
        await self.wait_random(0.025, 0.125)
        await self.page.mouse.up()

    async def click_element(self, locator: BSLocator, timeout: float = 10) -> None:
        """Hace clic en un elemento."""
        await self.page.locator(self.get_pw_locator(locator)).click(timeout=timeout*1000)

    async def click_nth_element(self, locator: BSLocator, index: int, timeout: float = 10) -> None:
        """Hace clic en el elemento en la posición especificada."""
        await self.page.locator(self.get_pw_locator(locator)).nth(index).click(timeout=timeout*1000)

    async def click_element_by_partial_texts(self, locator: BSLocator, partial_containing_texts: list[str],
                                             partial_non_containing_texts: list[str] = None, 
                                             timeout: float = 10) -> bool:
        """
        Hace clic en un elemento que contenga ciertos textos y no contenga otros.
        
        Args:
            locator: El locator base
            partial_containing_texts: Lista de textos que debe contener
            partial_non_containing_texts: Lista de textos que NO debe contener
            timeout: Timeout en segundos
        """
        await self.wait_element_to_be_present(locator, timeout)
        loc_to_click: Locator = self.page.locator(self.get_pw_locator(locator))

        try:
            for pt in partial_containing_texts:
                loc_to_click = loc_to_click.filter(has_text=pt)
            for pt in partial_non_containing_texts if partial_non_containing_texts is not None else []:
                loc_to_click = loc_to_click.filter(has_not_text=pt)
            await loc_to_click.first.click(timeout=timeout*1000)
            return True
        except TimeoutError:
            return False

    # ========== Métodos de entrada de texto ==========
    
    async def clear(self, locator: BSLocator) -> None:
        """Limpia el contenido de un input."""
        await self.page.locator(self.get_pw_locator(locator)).fill("")

    async def clear_input(self, input_elem: Locator, timeout: float = 10):
        """Limpia un input seleccionando todo y borrando."""
        if await input_elem.input_value(timeout=timeout*1000):
            await input_elem.click(click_count=3)
            await self.wait_random(0.1, 0.2)
            await input_elem.press('Backspace')

    async def human_send_keys_and_press_enter(self, locator: BSLocator, content: str, timeout: float = 10):
        await self.human_send_keys(locator, content, timeout)
        await self.wait_static(0.075)
        await self.page.locator(self.get_pw_locator(locator)).press('Enter')

    async def human_send_keys(self, locator: BSLocator, content: str, timeout: float = 10) -> None:
        """
        Envía teclas de forma humanizada (con delays aleatorios).
        
        Args:
            locator: El locator del elemento input
            content: El texto a escribir
            timeout: Timeout en segundos
        """
        min_delay: float = 0.0187
        max_delay: float = 0.123
        input_element: Locator = self.page.locator(self.get_pw_locator(locator))
        await input_element.focus()
        await self.clear_input(input_element, timeout)
        for char in content:
            await input_element.type(char)
            await self.wait_random(min_delay, max_delay)

    async def clear_and_send_keys(self, locator: BSLocator, value: Any) -> None:
        """Limpia un input y escribe nuevo contenido de forma humanizada."""
        await self.clear(locator)
        await self.human_send_keys(locator, str(value))

    # ========== Métodos de scroll ==========
    
    async def mouse_wheel_scroll(self, locator: BSLocator, timeout: float = 10) -> None:
        """Hace scroll con la rueda del mouse hasta que el elemento sea visible."""
        element_handle = self.page.locator(self.get_pw_locator(locator))
        elem_top_pos = await element_handle.evaluate("el => el.offsetTop")
        current_scroll = await self.page.evaluate("() => window.scrollY")
        await self.page.mouse.wheel(0, elem_top_pos - current_scroll)
        await self.wait_element_to_be_visible(locator, timeout)

    async def scroll_into_view(self, locator: BSLocator, timeout: float = 10) -> None:
        await self.wait_element_to_be_present(locator, timeout=timeout)
        elem_handle = self.get_pw_locator(locator)
        await self.page.evaluate("""
            (element) => {
                const rect = element.getBoundingClientRect();
                const elementCenterY = rect.top + rect.height / 2;
                const viewportCenterY = window.innerHeight / 2;
                window.scrollBy(0, elementCenterY - viewportCenterY);
            }
        """, elem_handle)


    async def get_current_url(self) -> str:
        """Obtiene la URL actual de la página."""
        return self.page.url
    # ========== Métodos de limpieza ==========
    
    async def quit(self):
        """Cierra el navegador y limpia los recursos."""
        if hasattr(self, '_camoufox_instance') and self._camoufox_instance:
            await self._camoufox_instance.__aexit__(None, None, None)
            self._camoufox_instance = None
            self.browser = None
            self.page = None

    # ========== Context manager support ==========
    
    async def __aenter__(self):
        """Soporte para async with."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Soporte para async with."""
        await self.quit()

    def __del__(self):
        """
        Limpieza al destruir la instancia.
        Nota: Es mejor usar quit() explícitamente o el context manager.
        """
        if hasattr(self, '_camoufox_instance') and self._camoufox_instance:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.quit())
                else:
                    loop.run_until_complete(self.quit())
            except Exception:
                pass
