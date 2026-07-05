#!/usr/bin/env python3
"""crawl — Crawl a website using Scrapy and extract links/content.

Usage:
    crawl <url> [max_pages] [--output file.json] [--follow] [--selector css]
"""
import argparse
import json
import sys

from scrapy.crawler import CrawlerProcess
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy import Selector


class QuickSpider(CrawlSpider):
    name = "quick_spider"

    custom_settings = {
        "LOG_LEVEL": "WARNING",
        "CONCURRENT_REQUESTS": 8,
        "DOWNLOAD_DELAY": 0.5,
        "AUTOTHROTTLE_ENABLED": True,
        "ROBOTSTXT_OBEY": True,
        "USER_AGENT": "AgenticSpace-Sandbox/1.0 (+https://github.com/HUB-Agentic-Space)",
    }

    def __init__(self, start_url="", max_pages=10, follow=False, selector=None, *args, **kwargs):
        self.start_urls = [start_url]
        self.allowed_domains = [self._extract_domain(start_url)]
        self.max_pages = int(max_pages)
        self.selector = selector
        self.results = []
        self.page_count = 0

        if follow:
            self.rules = [Rule(LinkExtractor(allow_domains=self.allowed_domains), callback="parse_item", follow=True)]
        else:
            self.rules = [Rule(LinkExtractor(allow_domains=self.allowed_domains), callback="parse_item", follow=False)]

        super().__init__(*args, **kwargs)

    def _extract_domain(self, url):
        from urllib.parse import urlparse
        return urlparse(url).netloc

    def parse_item(self, response):
        if self.page_count >= self.max_pages:
            raise StopIteration

        self.page_count += 1
        item = {
            "url": response.url,
            "title": response.css("title::text").get(default=""),
            "status": response.status,
        }

        if self.selector:
            elements = response.css(self.selector).getall()
            item["extracted"] = elements
        else:
            item["text"] = " ".join(response.css("body *::text").getall())[:2000]

        self.results.append(item)
        return item


def main():
    parser = argparse.ArgumentParser(description="Crawl a website with Scrapy")
    parser.add_argument("url", help="Starting URL")
    parser.add_argument("max_pages", nargs="?", type=int, default=10, help="Max pages to crawl (default: 10)")
    parser.add_argument("--output", "-o", default=None, help="Output JSON file")
    parser.add_argument("--follow", action="store_true", help="Follow links recursively")
    parser.add_argument("--selector", "-s", default=None, help="CSS selector to extract from each page")
    args = parser.parse_args()

    process = CrawlerProcess(settings={
        "LOG_LEVEL": "WARNING",
    })

    spider = process.create_crawler(QuickSpider)
    process.crawl(spider, start_url=args.url, max_pages=args.max_pages,
                  follow=args.follow, selector=args.selector)
    process.start()

    results = spider.spider.results if hasattr(spider.spider, "results") else []

    output = json.dumps(results, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Crawled {len(results)} pages → {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
