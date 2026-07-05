#!/usr/bin/env python3
"""map — Discover all URLs on a website instantly.

Usage:
    map <url> [--search term] [--format json|text] [--output file]
"""
import argparse
import json
import sys
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup


def extract_links(url, search_term=None):
    """Extract all links from a webpage."""
    headers = {
        "User-Agent": "AgenticSpace-Sandbox/1.0 (+https://github.com/HUB-Agentic-Space)"
    }
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    
    soup = BeautifulSoup(resp.text, "lxml")
    base_domain = urlparse(url).netloc
    links = []
    
    for a in soup.find_all("a", href=True):
        href = a["href"]
        absolute_url = urljoin(url, href)
        parsed = urlparse(absolute_url)
        
        # Only include links from the same domain
        if parsed.netloc == base_domain:
            title = a.get_text(strip=True)
            description = title  # Use title as description for now
            
            link_data = {
                "url": absolute_url,
                "title": title,
                "description": description
            }
            
            # Filter by search term if provided
            if search_term:
                if search_term.lower() in title.lower() or search_term.lower() in absolute_url.lower():
                    links.append(link_data)
            else:
                links.append(link_data)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_links = []
    for link in links:
        if link["url"] not in seen:
            seen.add(link["url"])
            unique_links.append(link)
    
    return unique_links


def main():
    parser = argparse.ArgumentParser(description="Discover all URLs on a website")
    parser.add_argument("url", help="Target URL")
    parser.add_argument("--search", "-s", default=None, help="Filter URLs by search term")
    parser.add_argument("--format", choices=["json", "text"], default="json",
                        help="Output format (default: json)")
    parser.add_argument("--output", "-o", default=None, help="Write to file instead of stdout")
    parser.add_argument("--timeout", type=int, default=30, help="Request timeout in seconds")
    args = parser.parse_args()

    links = extract_links(args.url, args.search)
    
    # Sort by relevance if search term is provided
    if args.search:
        links.sort(key=lambda x: (
            args.search.lower() in x["title"].lower(),
            args.search.lower() in x["url"].lower()
        ), reverse=True)
    
    if args.format == "text":
        lines = [f"URL: {args.url}", f"Links found: {len(links)}", ""]
        for i, link in enumerate(links, 1):
            lines.append(f"{i}. {link['title']}")
            lines.append(f"   URL: {link['url']}")
            if link['description']:
                lines.append(f"   Description: {link['description']}")
            lines.append("")
        output = "\n".join(lines)
    else:
        output = json.dumps({
            "url": args.url,
            "links": links
        }, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
