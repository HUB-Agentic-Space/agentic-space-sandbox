#!/usr/bin/env python3
"""markdown-scrape — Get LLM-ready markdown data from any website.

Usage:
    markdown-scrape <url> [--only-main-content] [--output file]
"""
import argparse
import sys
import requests
from bs4 import BeautifulSoup
from html2text import HTML2Text


def html_to_markdown(html, only_main_content=False):
    """Convert HTML to markdown."""
    h = HTML2Text()
    h.ignore_links = False
    h.ignore_images = False
    h.ignore_emphasis = False
    h.body_width = 0  # Don't wrap lines
    
    if only_main_content:
        # Try to extract main content
        soup = BeautifulSoup(html, "lxml")
        
        # Try common main content selectors
        main_selectors = [
            "main",
            "article",
            "[role='main']",
            ".content",
            "#content",
            ".post-content",
            ".article-content",
            "main article"
        ]
        
        main_elem = None
        for selector in main_selectors:
            main_elem = soup.select_one(selector)
            if main_elem:
                break
        
        if main_elem:
            html = str(main_elem)
        else:
            # Fallback: remove nav, header, footer, sidebar
            for tag in soup.find_all(["nav", "header", "footer", "aside", "sidebar"]):
                tag.decompose()
            html = str(soup)
    
    return h.handle(html)


def main():
    parser = argparse.ArgumentParser(description="Get LLM-ready markdown from any website")
    parser.add_argument("url", help="Target URL")
    parser.add_argument("--only-main-content", action="store_true",
                        help="Extract only main content, skip navigation/footer")
    parser.add_argument("--output", "-o", default=None, help="Write to file instead of stdout")
    parser.add_argument("--timeout", type=int, default=30, help="Request timeout in seconds")
    args = parser.parse_args()

    headers = {
        "User-Agent": "AgenticSpace-Sandbox/1.0 (+https://github.com/HUB-Agentic-Space)"
    }
    resp = requests.get(args.url, headers=headers, timeout=args.timeout)
    resp.raise_for_status()

    markdown = html_to_markdown(resp.text, args.only_main_content)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(markdown)
        print(f"Written to {args.output}", file=sys.stderr)
    else:
        print(markdown)


if __name__ == "__main__":
    main()
