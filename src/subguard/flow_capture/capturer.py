"""Playwright-based capture of public, ordered web flows."""

from __future__ import annotations

import ipaddress
import json
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import Browser, Page, Playwright, sync_playwright

from .models import CapturedFlow, CapturedScreen


class InvalidPublicUrlError(ValueError):
    """Raised when a URL is not clearly a public HTTP(S) URL."""


def validate_public_url(url: str) -> str:
    """Validate a URL without allowing credentials or obvious private hosts."""
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise InvalidPublicUrlError("Only public http:// and https:// URLs are allowed.")
    if parsed.username or parsed.password:
        raise InvalidPublicUrlError("URLs containing credentials are not allowed.")

    hostname = parsed.hostname.rstrip(".").lower()
    if hostname in {"localhost", "localhost.localdomain"} or hostname.endswith(".local"):
        raise InvalidPublicUrlError("Local hostnames are not allowed.")

    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        address = None
    if address and (address.is_private or address.is_loopback or address.is_link_local):
        raise InvalidPublicUrlError("Private, loopback, and link-local hosts are not allowed.")
    return url


class FlowCapturer:
    """Capture a public flow by following explicitly supplied next selectors."""

    def __init__(
        self,
        output_dir: str | Path,
        *,
        headless: bool = True,
        timeout_ms: int = 30_000,
    ) -> None:
        self.output_dir = Path(output_dir)
        self.headless = headless
        self.timeout_ms = timeout_ms

    def capture(self, url: str, flow_type: str, next_selectors: list[str]) -> CapturedFlow:
        """Capture the initial page and each screen reached by a next selector."""
        source_url = validate_public_url(url)
        if flow_type not in {"sign-up", "cancellation"}:
            raise ValueError("flow_type must be 'sign-up' or 'cancellation'.")

        self.output_dir.mkdir(parents=True, exist_ok=True)
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=self.headless)
            try:
                screens = self._capture_with_browser(
                    browser, source_url, flow_type, next_selectors
                )
            finally:
                browser.close()

        flow = CapturedFlow(
            source_url=source_url,
            flow_type=flow_type,
            output_dir=str(self.output_dir),
            screens=tuple(screens),
        )
        (self.output_dir / "manifest.json").write_text(
            json.dumps(flow.to_dict(), indent=2),
            encoding="utf-8",
        )
        return flow

    def _capture_with_browser(
        self,
        browser: Browser,
        source_url: str,
        flow_type: str,
        next_selectors: list[str],
    ) -> list[CapturedScreen]:
        context = browser.new_context()
        page = context.new_page()
        page.set_default_timeout(self.timeout_ms)
        screens: list[CapturedScreen] = []
        try:
            page.goto(source_url, wait_until="domcontentloaded")
            screens.append(self._save_screen(page, 1))
            for order, selector in enumerate(next_selectors, start=2):
                page.locator(selector).first.click()
                page.wait_for_load_state("domcontentloaded")
                screens.append(self._save_screen(page, order))
        finally:
            context.close()
        return screens

    def _save_screen(self, page: Page, order: int) -> CapturedScreen:
        screen_dir = self.output_dir / f"screen-{order:03d}"
        screen_dir.mkdir(parents=True, exist_ok=True)
        dom_path = screen_dir / "dom.html"
        text_path = screen_dir / "visible-text.txt"
        screenshot_path = screen_dir / "screenshot.png"

        dom_path.write_text(page.content(), encoding="utf-8")
        text_path.write_text(page.locator("body").inner_text(), encoding="utf-8")
        page.screenshot(path=str(screenshot_path), full_page=True)
        return CapturedScreen(
            order=order,
            url=page.url,
            dom_path=str(dom_path),
            visible_text_path=str(text_path),
            screenshot_path=str(screenshot_path),
        )

