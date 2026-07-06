#!/usr/bin/env python3
"""deep-research — Perform comprehensive research on a topic using search, crawl, and extraction.

Usage:
    deep-research <query> [--max-pages N] [--output file] [--format json|markdown]
"""
import argparse
import json
import sys
from urllib.parse import quote, parse_qs, urlparse, unquote
import requests
from bs4 import BeautifulSoup
from html2text import HTML2Text


def resolve_ddg_url(raw_url):
    """Resolve a DuckDuckGo redirect URL to the actual target URL.

    DuckDuckGo returns links like:
      //duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.com&rut=...
    This function extracts and returns the decoded 'uddg' value.
    Falls back to prepending 'https:' if the URL is schemeless.
    """
    if not raw_url:
        return ""

    url = raw_url
    if url.startswith("//"):
        url = "https:" + url

    parsed = urlparse(url)
    if "duckduckgo.com" in (parsed.hostname or "") and parsed.query:
        qs = parse_qs(parsed.query)
        if "uddg" in qs:
            return unquote(qs["uddg"][0])

    return url


def search_duckduckgo(query, limit=10):
    """Search using DuckDuckGo HTML."""
    url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
    headers = {
        "User-Agent": "AgenticSpace-Sandbox/1.0 (+https://github.com/HUB-Agentic-Space)"
    }
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    
    soup = BeautifulSoup(resp.text, "lxml")
    results = []
    
    for result in soup.select(".result")[:limit]:
        title_elem = result.select_one(".result__a")
        snippet_elem = result.select_one(".result__snippet")
        
        if title_elem:
            raw_url = title_elem.get("href", "")
            resolved_url = resolve_ddg_url(raw_url)
            results.append({
                "title": title_elem.get_text(strip=True),
                "url": resolved_url,
                "snippet": snippet_elem.get_text(strip=True) if snippet_elem else ""
            })
    
    return results


def fetch_page_content(url, format="markdown", timeout=30):
    """Fetch and extract content from a URL."""
    headers = {
        "User-Agent": "AgenticSpace-Sandbox/1.0 (+https://github.com/HUB-Agentic-Space)"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=timeout)
        resp.raise_for_status()
        
        if format == "markdown":
            h = HTML2Text()
            h.ignore_links = False
            h.ignore_images = False
            h.body_width = 0
            content = h.handle(resp.text)
        else:
            soup = BeautifulSoup(resp.text, "lxml")
            for script in soup(["script", "style"]):
                script.decompose()
            content = soup.get_text(separator="\n", strip=True)
        
        return {
            "url": url,
            "content": content[:10000],  # Limit content length
            "success": True
        }
    except Exception as e:
        return {
            "url": url,
            "error": str(e),
            "success": False
        }


def main():
    parser = argparse.ArgumentParser(description="Perform comprehensive research on a topic")
    parser.add_argument("query", help="Research query/topic")
    parser.add_argument("--max-pages", "-m", type=int, default=5, help="Max pages to research (default: 5)")
    parser.add_argument("--format", choices=["json", "markdown"], default="markdown",
                        help="Output format (default: markdown)")
    parser.add_argument("--output", "-o", default=None, help="Write to file instead of stdout")
    parser.add_argument("--timeout", type=int, default=30, help="Request timeout in seconds")
    args = parser.parse_args()

    # Step 1: Search for relevant pages
    print(f"Searching for: {args.query}", file=sys.stderr)
    search_results = search_duckduckgo(args.query, limit=args.max_pages)
    print(f"Found {len(search_results)} results", file=sys.stderr)

    # Step 2: Fetch content from each result
    research_data = {
        "query": args.query,
        "search_results": search_results,
        "content": []
    }

    for i, result in enumerate(search_results, 1):
        print(f"Fetching content {i}/{len(search_results)}: {result['url']}", file=sys.stderr)
        page_data = fetch_page_content(result["url"], args.format, args.timeout)
        page_data["title"] = result["title"]
        page_data["snippet"] = result["snippet"]
        research_data["content"].append(page_data)

    # Step 3: Format output
    if args.format == "json":
        output = json.dumps(research_data, ensure_ascii=False, indent=2)
    else:
        lines = [
            f"# Deep Research: {args.query}",
            f"",
            f"## Search Results ({len(search_results)} pages)",
            f""
        ]
        
        for i, result in enumerate(search_results, 1):
            lines.append(f"### {i}. {result['title']}")
            lines.append(f"**URL:** {result['url']}")
            lines.append(f"**Snippet:** {result['snippet']}")
            lines.append("")
            
            # Find corresponding content
            content_data = next((c for c in research_data["content"] if c["url"] == result["url"]), None)
            if content_data and content_data.get("success"):
                lines.append("**Content:**")
                lines.append(content_data["content"][:3000])
                lines.append("")
            elif content_data:
                lines.append(f"**Error:** {content_data.get('error', 'Unknown error')}")
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
