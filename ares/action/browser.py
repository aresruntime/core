"""Playwright browser wrapper used by the action layer."""

from __future__ import annotations

import logging

logger = logging.getLogger("ares.browser")


class Browser:
    """Thin wrapper over Playwright, lazy-initialized."""

    def __init__(self):
        self._page = None
        self._browser = None
        self._playwright = None

    def _ensure(self):
        if self._page is not None:
            return
        from playwright.sync_api import sync_playwright
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(headless=True)
        self._page = self._browser.new_page()

    def navigate(self, url: str) -> str:
        self._ensure()
        self._page.goto(url, wait_until="domcontentloaded")
        return f"navigated to {url}"

    def click(self, selector: str) -> str:
        self._ensure()
        self._page.click(selector)
        return f"clicked {selector}"

    def type(self, selector: str, text: str) -> str:
        self._ensure()
        self._page.fill(selector, text)
        return f"typed into {selector}"

    def extract(self, target: str) -> str:
        self._ensure()
        try:
            handle = self._page.locator(target).first
            return handle.inner_text()[:2000]
        except Exception:
            return self._page.content()[:2000]

    def close(self) -> None:
        if self._browser is not None:
            self._browser.close()
        if self._playwright is not None:
            self._playwright.stop()
