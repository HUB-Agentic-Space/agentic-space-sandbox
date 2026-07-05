# AgenticSpace Sandbox

Docker image for **web scraping, data extraction, feed search, and RSS syndication** — all via command-line tools, no GUI required.

## Docker Hub

```bash
docker pull carlosdelfino/agenticspace-sandbox:latest
```

## Included Tools

### Native CLI Tools
| Tool | Description |
|------|-------------|
| `curl` | HTTP requests, fetch raw HTML/JSON |
| `wget` | Download files, recursive fetch |
| `jq` | JSON filtering, slicing, formatting |
| `htmlq` | Parse HTML with CSS selectors (Rust) |
| `xidel` | XPath, CSS3 selectors on HTML/XML |

### Python Tools (custom scripts)
| Command | Description |
|---------|-------------|
| `scrape-url <url> [selector]` | Fetch URL, extract via CSS selector |
| `extract-data <url>` | Extract JSON-LD, OpenGraph, meta tags |
| `find-feeds <url>` | Discover RSS/Atom feeds on a page |
| `parse-feed <feed_url>` | Parse and display feed entries |
| `gen-feed <json_file>` | Generate RSS 2.0 feed from JSON |
| `crawl <url> [max_pages]` | Crawl site with Scrapy |
| `screenshot <url> [output.png]` | Headless screenshot with Playwright |
| `api-fetch <url> [jq_filter]` | Fetch JSON API, filter with jq |
| `search-web <query>` | Search the web and get full content |
| `map <url>` | Discover all URLs on a website |
| `batch-scrape <urls_file>` | Scrape multiple URLs at once |
| `markdown-scrape <url>` | Get LLM-ready markdown from any website |
| `interact <url> --prompt <cmd>` | Interact with webpage using browser automation |
| `deep-research <query>` | Perform comprehensive research on a topic |

### Python Libraries
- **Scrapy** — large-scale crawling framework
- **Beautiful Soup** + **lxml** — HTML parsing
- **Playwright** — headless browser automation (Chromium installed)
- **feedparser** — RSS/Atom feed parsing
- **feedgenerator** — RSS/Atom feed generation
- **extruct** — structured data extraction (JSON-LD, microdata, RDFa)
- **httpx** / **aiohttp** — async HTTP clients
- **selectolax** — fast HTML parsing
- **pyquery** — jQuery-like syntax for Python

## Usage Examples

```bash
# Fetch and parse a page
docker run --rm carlosdelfino/agenticspace-sandbox scrape-url https://example.com "h1"

# Extract structured data
docker run --rm carlosdelfino/agenticspace-sandbox extract-data https://example.com

# Find RSS feeds
docker run --rm carlosdelfino/agenticspace-sandbox find-feeds https://example.com --check

# Parse a feed
docker run --rm carlosdelfino/agenticspace-sandbox parse-feed https://example.com/feed.xml --limit 5

# Crawl a site
docker run --rm carlosdelfino/agenticspace-sandbox crawl https://example.com 20 --follow -o results.json

# Take a screenshot
docker run --rm -v $(pwd):/workspace carlosdelfino/agenticspace-sandbox screenshot https://example.com /workspace/out.png --full-page

# Fetch JSON API with jq filter
docker run --rm carlosdelfino/agenticspace-sandbox api-fetch https://api.github.com/repos/HUB-Agentic-Space/agentic-space-sandbox '.full_name'

# Search the web
docker run --rm carlosdelfino/agenticspace-sandbox search-web "python web scraping" --limit 5

# Map website URLs
docker run --rm carlosdelfino/agenticspace-sandbox map https://example.com --search pricing

# Get LLM-ready markdown
docker run --rm carlosdelfino/agenticspace-sandbox markdown-scrape https://example.com --only-main-content

# Deep research on a topic
docker run --rm carlosdelfino/agenticspace-sandbox deep-research "AI trends 2024" --max-pages 5

# Use native tools directly
docker run --rm carlosdelfino/agenticspace-sandbox curl -s https://example.com | htmlq 'title' --text
docker run --rm carlosdelfino/agenticspace-sandbox curl -s https://api.github.com | jq '.current_user_url'

# Interactive shell
docker run -it carlosdelfino/agenticspace-sandbox bash
```

## Build

```bash
docker build -t carlosdelfino/agenticspace-sandbox:latest .
```

## License

MIT
