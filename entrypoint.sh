#!/bin/bash
set -e

case "$1" in
    --help|-h)
        echo "AgenticSpace Sandbox — Web Scraping & RSS CLI Toolkit"
        echo ""
        echo "Available commands:"
        echo "  scrape-url <url> [css_selector]   — Fetch URL and extract content"
        echo "  extract-data <url>                — Extract structured data (JSON-LD, OG, meta)"
        echo "  find-feeds  <url>                 — Discover RSS/Atom feeds on a page"
        echo "  parse-feed  <feed_url_or_file>    — Parse and display feed entries"
        echo "  gen-feed    <json_file>           — Generate RSS feed from JSON data"
        echo "  crawl       <url> [max_pages]     — Crawl site with Scrapy"
        echo "  screenshot  <url> [output.png]    — Take headless screenshot with Playwright"
        echo "  api-fetch   <url> [jq_filter]     — Fetch JSON API and filter with jq"
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
