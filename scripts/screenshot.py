#!/usr/bin/env python3
"""screenshot — Take a headless screenshot of a webpage using Playwright.

Usage:
    screenshot <url> [output.png] [--width 1280] [--height 720] [--full-page] [--wait ms]
"""
import argparse
import sys

from playwright.sync_api import sync_playwright


def main():
    parser = argparse.ArgumentParser(description="Take headless screenshot with Playwright")
    parser.add_argument("url", help="Target URL")
    parser.add_argument("output", nargs="?", default="screenshot.png", help="Output file (default: screenshot.png)")
    parser.add_argument("--width", type=int, default=1280, help="Viewport width")
    parser.add_argument("--height", type=int, default=720, help="Viewport height")
    parser.add_argument("--full-page", action="store_true", help="Capture full page")
    parser.add_argument("--wait", type=int, default=2000, help="Wait time in ms before screenshot")
    parser.add_argument("--user-agent", "-u", default=None, help="Custom User-Agent")
    args = parser.parse_args()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": args.width, "height": args.height},
            user_agent=args.user_agent or "AgenticSpace-Sandbox/1.0 (+https://github.com/HUB-Agentic-Space)",
        )
        page = context.new_page()
        page.goto(args.url, wait_until="networkidle")
        page.wait_for_timeout(args.wait)
        page.screenshot(path=args.output, full_page=args.full_page)
        browser.close()

    print(f"Screenshot saved to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
