#!/usr/bin/env python3
"""search-web — Search the web and get full content from results.

Usage:
    search-web <query> [--limit N] [--format json|text] [--output file]
"""
import argparse
import json
import sys
from urllib.parse import quote, parse_qs, urlparse, unquote
import requests
from bs4 import BeautifulSoup


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


def search_duckduckgo(query, limit=5):
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
        url_elem = result.select_one(".result__url")
        
        if title_elem:
            raw_url = title_elem.get("href", "")
            resolved_url = resolve_ddg_url(raw_url)
            results.append({
                "title": title_elem.get_text(strip=True),
                "url": resolved_url,
                "snippet": snippet_elem.get_text(strip=True) if snippet_elem else "",
                "display_url": url_elem.get_text(strip=True) if url_elem else ""
            })
    
    return results


def fetch_content(url, timeout=30):
    """Fetch and extract content from a URL."""
    headers = {
        "User-Agent": "AgenticSpace-Sandbox/1.0 (+https://github.com/HUB-Agentic-Space)"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=timeout)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extract main content
        text = soup.get_text(separator="\n", strip=True)
        return text[:5000]  # Limit to 5000 chars
    except Exception as e:
        return f"Error fetching content: {str(e)}"


def main():
    parser = argparse.ArgumentParser(description="Search the web and get full content from results")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--limit", "-l", type=int, default=5, help="Number of results (default: 5)")
    parser.add_argument("--format", choices=["json", "text"], default="json",
                        help="Output format (default: json)")
    parser.add_argument("--output", "-o", default=None, help="Write to file instead of stdout")
    parser.add_argument("--no-content", action="store_true", help="Don't fetch full content from results")
    args = parser.parse_args()

    # Search
    results = search_duckduckgo(args.query, args.limit)
    
    # Fetch content for each result
    if not args.no_content:
        for result in results:
            if result["url"]:
                result["markdown"] = fetch_content(result["url"])
    
    # Format output
    if args.format == "text":
        lines = [f"Query: {args.query}", f"Results: {len(results)}", ""]
        for i, result in enumerate(results, 1):
            lines.append(f"{i}. {result['title']}")
            lines.append(f"   URL: {result['url']}")
            if result.get("snippet"):
                lines.append(f"   Snippet: {result['snippet']}")
            if result.get("markdown"):
                lines.append(f"   Content: {result['markdown'][:500]}...")
            lines.append("")
        output = "\n".join(lines)
    else:
        output = json.dumps({
            "query": args.query,
            "results": results
        }, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
