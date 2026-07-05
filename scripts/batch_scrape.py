#!/usr/bin/env python3
"""batch-scrape — Scrape multiple URLs at once.

Usage:
    batch-scrape <urls_file> [--format markdown|json|html] [--output file]
"""
import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from bs4 import BeautifulSoup
from html2text import HTML2Text


def scrape_url(url, format="markdown", timeout=30):
    """Scrape a single URL and return formatted content."""
    headers = {
        "User-Agent": "AgenticSpace-Sandbox/1.0 (+https://github.com/HUB-Agentic-Space)"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=timeout)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, "lxml")
        title = soup.title.string if soup.title else ""
        
        if format == "markdown":
            h = HTML2Text()
            h.ignore_links = False
            h.ignore_images = False
            content = h.handle(resp.text)
        elif format == "json":
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            content = {
                "title": title,
                "text": soup.get_text(separator="\n", strip=True)[:10000],
                "html": str(soup)[:5000]
            }
        else:  # html
            content = resp.text
        
        return {
            "url": url,
            "title": title,
            "status": resp.status_code,
            "content": content
        }
    except Exception as e:
        return {
            "url": url,
            "title": "",
            "status": "error",
            "error": str(e)
        }


def main():
    parser = argparse.ArgumentParser(description="Scrape multiple URLs at once")
    parser.add_argument("urls_file", help="File containing URLs (one per line)")
    parser.add_argument("--format", choices=["markdown", "json", "html"], default="markdown",
                        help="Output format (default: markdown)")
    parser.add_argument("--output", "-o", default=None, help="Write to file instead of stdout")
    parser.add_argument("--timeout", type=int, default=30, help="Request timeout in seconds")
    parser.add_argument("--workers", type=int, default=5, help="Number of concurrent workers")
    args = parser.parse_args()

    # Read URLs from file
    with open(args.urls_file, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    if not urls:
        print("No URLs found in file", file=sys.stderr)
        sys.exit(1)

    # Scrape URLs in parallel
    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        future_to_url = {
            executor.submit(scrape_url, url, args.format, args.timeout): url
            for url in urls
        }
        
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                result = future.result()
                results.append(result)
                print(f"Scraped: {url}", file=sys.stderr)
            except Exception as e:
                results.append({
                    "url": url,
                    "status": "error",
                    "error": str(e)
                })
                print(f"Error scraping {url}: {e}", file=sys.stderr)

    # Format output
    if args.format == "json":
        output = json.dumps(results, ensure_ascii=False, indent=2)
    else:
        lines = [f"Batch Scrape Results: {len(results)} URLs", ""]
        for result in results:
            lines.append(f"URL: {result['url']}")
            lines.append(f"Title: {result.get('title', 'N/A')}")
            lines.append(f"Status: {result.get('status', 'N/A')}")
            if result.get("error"):
                lines.append(f"Error: {result['error']}")
            else:
                content = result.get("content", "")
                if isinstance(content, str):
                    lines.append(f"Content: {content[:500]}...")
                else:
                    lines.append(f"Content: {json.dumps(content, ensure_ascii=False)[:500]}...")
            lines.append("")
        output = "\n".join(lines)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
