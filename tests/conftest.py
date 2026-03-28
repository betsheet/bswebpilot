import pytest_asyncio
from bswebpilot.bsplaywright.bscmfx import BSCmfx


@pytest_asyncio.fixture(scope="function")
async def browser():
    """
    Fixture que inicializa BSCmfx en modo headless antes de cada test
    y lo cierra automáticamente al terminar.
    """
    async with BSCmfx(is_headless=True, humanize=False) as cmfx:
        yield cmfx

