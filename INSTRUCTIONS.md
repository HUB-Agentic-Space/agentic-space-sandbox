# AgenticSpace - INSTRUCTIONS

## Python Libraries
- **Scrapy** (>=2.11,<3) - Web crawling framework
- **BeautifulSoup4** (>=4.12) - HTML/XML parsing
- **lxml** (>=5.1) - Fast XML/HTML processing
- **requests** (>=2.31) - HTTP library
- **httpx** (>=0.27) - Async HTTP client
- **Playwright** (>=1.40) - Headless browser automation
- **feedparser** (>=6.0) - RSS/Atom feed parsing
- **feedgenerator** (>=2.1) - RSS feed generation
- **atoma** (>=0.0.17) - Atom feed parsing
- **selectolax** (>=0.3.21) - Fast HTML parser
- **cssselect** (>=1.2) - CSS selector parsing
- **pyquery** (>=2.0) - jQuery-like HTML parsing
- **extruct** (>=0.16.0) - Structured data extraction (JSON-LD, OpenGraph, etc.)
- **w3lib** (>=2.1) - Web utility functions
- **PyYAML** (>=6.0) - YAML parsing
- **rich** (>=13.7) - Terminal formatting
- **aiohttp** (>=3.9) - Async HTTP client/server
- **aiodns** (>=3.1) - Async DNS resolver
- **aiofiles** (>=23.2) - Async file operations
- **tldextract** (>=5.1) - Domain name extraction
- **urllib3** (>=2.1) - HTTP library with connection pooling
- **tenacity** (>=8.2) - Retry library
- **fake-useragent** (>=1.4) - User-Agent spoofing
- **python-dateutil** (>=2.9) - Date parsing

## CLI Tools
- **htmlq** - CSS selector-based HTML extraction (Rust-based)
- **xidel** - HTML/XML XPath & CSS selector extraction
- **jq** - JSON processor (for API filtering)

## Custom Scripts (Available in /opt/agentic-scripts/)
All scripts can be called directly by name (they are in PATH):

### api-fetch
Fetch JSON API and optionally filter with jq-like syntax.
```bash
api-fetch <url> [jq_filter] [--header key=val ...] [--output file] [--timeout seconds]
```
**Examples:**
- `api-fetch https://api.example.com/data`
- `api-fetch https://api.example.com/data '.items[] | {name, value}'`
- `api-fetch https://api.example.com/data --header "Authorization=Bearer token" --output result.json`

**Help:** `api-fetch --help`

### crawl
Crawl a website using Scrapy and extract links/content.
```bash
crawl <url> [max_pages] [--output file.json] [--follow] [--selector css]
```
**Examples:**
- `crawl https://example.com 10`
- `crawl https://example.com 50 --follow --output results.json`
- `crawl https://example.com 20 --selector 'article h2' --follow`

**Help:** `crawl --help`

### extract-data
Extract structured data from a webpage (JSON-LD, OpenGraph, meta tags).
```bash
extract-data <url> [--format json|text] [--output file] [--timeout seconds]
```
**Examples:**
- `extract-data https://example.com`
- `extract-data https://example.com --format text --output metadata.txt`
- `extract-data https://example.com --format json --output structured.json`

**Help:** `extract-data --help`

### find-feeds
Discover RSS/Atom feeds on a webpage.
```bash
find-feeds <url> [--output file] [--check] [--format json|text]
```
**Examples:**
- `find-feeds https://example.com`
- `find-feeds https://example.com --check --format json`
- `find-feeds https://example.com --output feeds.txt`

**Help:** `find-feeds --help`

### gen-feed
Generate an RSS 2.0 feed from a JSON file.
```bash
gen-feed <json_file> [--output file.rss]
```
**JSON Format:**
```json
{
  "title": "My Feed",
  "link": "https://example.com",
  "description": "Feed description",
  "language": "en",
  "entries": [
    {
      "title": "Entry title",
      "link": "https://example.com/1",
      "description": "Entry content",
      "published": "2024-01-01T00:00:00Z",
      "author": "Author Name"
    }
  ]
}
```
**Examples:**
- `gen-feed data.json --output feed.rss`
- `gen-feed data.json`

**Help:** `gen-feed --help`

### parse-feed
Parse and display RSS/Atom feed entries.
```bash
parse-feed <feed_url_or_file> [--limit N] [--format json|text|csv] [--output file]
```
**Examples:**
- `parse-feed https://example.com/feed.xml`
- `parse-feed https://example.com/feed.xml --limit 10 --format json`
- `parse-feed feed.xml --format csv --output entries.csv`

**Help:** `parse-feed --help`

### scrape-url
Fetch a URL and optionally extract content via CSS selector.
```bash
scrape-url <url> [css_selector] [--format text|html|json] [--output file] [--user-agent string] [--timeout seconds]
```
**Examples:**
- `scrape-url https://example.com`
- `scrape-url https://example.com 'article.content' --format text`
- `scrape-url https://example.com 'h1' --format json --output titles.json`

**Help:** `scrape-url --help`

### screenshot
Take a headless screenshot of a webpage using Playwright.
```bash
screenshot <url> [output.png] [--width 1280] [--height 720] [--full-page] [--wait ms] [--user-agent string]
```
**Examples:**
- `screenshot https://example.com`
- `screenshot https://example.com screenshot.png --width 1920 --height 1080`
- `screenshot https://example.com --full-page --wait 5000`

**Help:** `screenshot --help`

### search-web
Search the web and get full content from results.
```bash
search-web <query> [--limit N] [--format json|text] [--output file] [--no-content]
```
**Examples:**
- `search-web "python web scraping"`
- `search-web "machine learning" --limit 10 --format json`
- `search-web "docker tutorial" --output results.json`

**Help:** `search-web --help`

### map
Discover all URLs on a website instantly.
```bash
map <url> [--search term] [--format json|text] [--output file]
```
**Examples:**
- `map https://example.com`
- `map https://example.com --search pricing`
- `map https://example.com --format json --output sitemap.json`

**Help:** `map --help`

### batch-scrape
Scrape multiple URLs at once.
```bash
batch-scrape <urls_file> [--format markdown|json|html] [--output file] [--workers N]
```
**Examples:**
- `batch-scrape urls.txt`
- `batch-scrape urls.txt --format json --output results.json`
- `batch-scrape urls.txt --format markdown --workers 10`

**Help:** `batch-scrape --help`

### markdown-scrape
Get LLM-ready markdown data from any website.
```bash
markdown-scrape <url> [--only-main-content] [--output file]
```
**Examples:**
- `markdown-scrape https://example.com`
- `markdown-scrape https://example.com --only-main-content --output article.md`

**Help:** `markdown-scrape --help`

### interact
Scrape a page, then interact with it using browser automation.
```bash
interact <url> --prompt "instruction" [--output file] [--screenshot file.png] [--format markdown|text|json]
```
**Examples:**
- `interact https://example.com --prompt "Click the first result"`
- `interact https://amazon.com --prompt "Search for mechanical keyboard" --screenshot result.png`
- `interact https://example.com --prompt "Scroll down" --format markdown`

**Help:** `interact --help`

### deep-research
Perform comprehensive research on a topic using search, crawl, and extraction.
```bash
deep-research <query> [--max-pages N] [--output file] [--format json|markdown]
```
**Examples:**
- `deep-research "climate change effects"`
- `deep-research "quantum computing" --max-pages 10 --format markdown`
- `deep-research "AI trends 2024" --output research.json`

**Help:** `deep-research --help`

## System Tools
- **curl** - Command-line HTTP client
- **wget** - Command-line HTTP downloader
- **git** - Version control
- **jq** - JSON processor

## Getting Help
For any Python library, you can use:
```bash
python -c "import library_name; help(library_name)"
```

For CLI tools, use the `--help` flag:
```bash
htmlq --help
xidel --help
jq --help
```

For custom scripts, use `--help`:
```bash
api-fetch --help
crawl --help
extract-data --help
find-feeds --help
gen-feed --help
parse-feed --help
scrape-url --help
screenshot --help
search-web --help
map --help
batch-scrape --help
markdown-scrape --help
interact --help
deep-research --help
```

## Environment Variables
- `PYTHONUNBUFFERED=1` - Unbuffered Python output
- `PYTHONDONTWRITEBYTECODE=1` - Don't write .pyc files
- `PLAYWRIGHT_BROWSERS_PATH=/opt/playwright-browsers` - Playwright browser location
- `LANG=C.UTF-8` - System locale
- `LC_ALL=C.UTF-8` - System locale
- `PUID=1000` - User ID for unprivileged user (LinuxServer images)
- `PGID=1000` - Group ID for unprivileged user (LinuxServer images)
- `TZ=America/Fortaleza` - Timezone (LinuxServer images)
- `OPENCLAW_CLI=1` - Enable CLI mode (bypasses LinuxServer init)

## Working Directory
Default working directory: `/workspace`

## Best Practices
1. Always use `--timeout` parameter for network requests to avoid hanging
2. Respect robots.txt when crawling (enabled by default in Scrapy)
3. Use appropriate User-Agent strings or the default provided
4. For large-scale crawling, use the `--follow` flag judiciously
5. When parsing feeds, consider using `--limit` to avoid processing huge feeds
6. Use `--output` parameter to save results to files for further processing

## Error Handling
All scripts return appropriate exit codes:
- 0: Success
- Non-zero: Error occurred

Check stderr for error messages and diagnostic information.
