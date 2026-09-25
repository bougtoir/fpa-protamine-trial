#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from playwright.async_api import async_playwright


async def capture(url: str, output: Path) -> None:
    async with async_playwright() as playwright:
        browser = await playwright.chromium.connect_over_cdp("http://localhost:29229")
        context = browser.contexts[0]
        page = await context.new_page()
        await page.goto(url, wait_until="networkidle", timeout=120_000)
        output.write_text(await page.content(), encoding="utf-8")
        await page.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Capture an authoritative web page through the session browser.")
    parser.add_argument("url")
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    asyncio.run(capture(args.url, args.output))


if __name__ == "__main__":
    main()
