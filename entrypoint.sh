#!/bin/bash
set -e

case "$1" in
    --help|-h)
        echo "AgenticSpace Sandbox — Web Scraping & RSS CLI Toolkit"
        echo ""
        echo "Available commands:"
        echo "  scrape-url     <url> [css_selector]   — Fetch URL and extract content"
        echo "  extract-data   <url>                — Extract structured data (JSON-LD, OG, meta)"
        echo "  find-feeds     <url>                 — Discover RSS/Atom feeds on a page"
        echo "  parse-feed     <feed_url_or_file>    — Parse and display feed entries"
        echo "  gen-feed       <json_file>           — Generate RSS feed from JSON data"
        echo "  crawl          <url> [max_pages]     — Crawl site with Scrapy"
        echo "  screenshot     <url> [output.png]    — Take headless screenshot with Playwright"
        echo "  api-fetch      <url> [jq_filter]     — Fetch JSON API and filter with jq"
        echo "  search-web     <query>               — Search the web and get full content"
        echo "  map            <url>                 — Discover all URLs on a website"
        echo "  batch-scrape   <urls_file>           — Scrape multiple URLs at once"
        echo "  markdown-scrape <url>                — Get LLM-ready markdown from any website"
        echo "  interact       <url> --prompt <cmd>  — Interact with webpage using browser automation"
        echo "  deep-research  <query>               — Perform comprehensive research on a topic"
        echo ""
        echo "RAG commands (living web index):"
        echo "  rag-index     <url>                  — Scrape & index a URL (embeddings if configured)"
        echo "  rag-search    <query>                — Search indexed content (semantic or keyword)"
        echo "  rag-update    [url] [--all]          — Check for content changes & re-index"
        echo "  rag-list                             — List all indexed sites"
        echo "  rag-status                           — Show RAG index statistics"
        echo "  rag-remove    <url>                  — Remove a site from the index"
        echo ""
        echo "Or run any shell command directly: docker run ... curl https://example.com"
        echo ""
        echo "Interactive shell: docker run -it carlosdelfino/agenticspace-sandbox bash"
        exit 0
        ;;
    bash|sh)
        exec "$@"
        ;;
    "")
        exec bash
        ;;
    *)
        exec "$@"
        ;;
esac
