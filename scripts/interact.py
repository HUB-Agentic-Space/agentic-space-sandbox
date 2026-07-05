#!/usr/bin/env python3
"""interact — Scrape a page, then interact with it using browser automation.

Usage:
    interact <url> --prompt "instruction" [--output file] [--screenshot file.png]
"""
import argparse
import json
import sys
from playwright.sync_api import sync_playwright
from html2text import HTML2Text


def execute_action(page, action):
    """Execute a browser action based on natural language instruction."""
    action_lower = action.lower()
    
    # Click actions
    if "click" in action_lower:
        # Try to find element by text or selector
        selector = action_lower.replace("click", "").strip()
        if not selector:
            # Try to find first clickable element
            page.click("a, button, [role='button'] >> visible=true >> nth=0")
        else:
            page.click(f"text={selector}")
    
    # Type actions
    elif "type" in action_lower or "enter" in action_lower or "write" in action_lower:
        text = action_lower.replace("type", "").replace("enter", "").replace("write", "").strip()
        page.fill("input[type='text'], input[type='search'], textarea >> visible=true >> nth=0", text)
    
    # Scroll actions
    elif "scroll" in action_lower:
        if "down" in action_lower:
            page.evaluate("window.scrollBy(0, 500)")
        elif "up" in action_lower:
            page.evaluate("window.scrollBy(0, -500)")
        else:
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    
    # Wait actions
    elif "wait" in action_lower:
        page.wait_for_timeout(2000)
    
    # Search actions
    elif "search" in action_lower:
        search_term = action_lower.replace("search", "").replace("for", "").strip()
        page.fill("input[type='search'], input[type='text'] >> visible=true >> nth=0", search_term)
        page.press("input[type='search'], input[type='text'] >> visible=true >> nth=0", "Enter")
    
    else:
        # Try to interpret as a selector click
        try:
            page.click(action)
        except:
            print(f"Could not execute action: {action}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Interact with a webpage using browser automation")
    parser.add_argument("url", help="Target URL")
    parser.add_argument("--prompt", "-p", required=True, help="Instruction for interaction (e.g., 'Click the first result')")
    parser.add_argument("--output", "-o", default=None, help="Write result to file")
    parser.add_argument("--screenshot", "-s", default=None, help="Save screenshot after interaction")
    parser.add_argument("--format", choices=["markdown", "text", "json"], default="markdown",
                        help="Output format (default: markdown)")
    parser.add_argument("--timeout", type=int, default=30, help="Page load timeout in seconds")
    args = parser.parse_args()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # Navigate to URL
            page.goto(args.url, timeout=args.timeout * 1000)
            page.wait_for_load_state("networkidle")
            
            # Execute the interaction
            execute_action(page, args.prompt)
            
            # Wait for any dynamic content
            page.wait_for_timeout(1000)
            
            # Get page content
            html = page.content()
            
            # Convert to requested format
            if args.format == "markdown":
                h = HTML2Text()
                h.ignore_links = False
                h.ignore_images = False
                h.body_width = 0
                content = h.handle(html)
            elif args.format == "json":
                content = {
                    "url": page.url,
                    "title": page.title(),
                    "content": html[:10000]
                }
                content = json.dumps(content, ensure_ascii=False, indent=2)
            else:
                content = page.inner_text("body")
            
            # Take screenshot if requested
            if args.screenshot:
                page.screenshot(path=args.screenshot, full_page=True)
                print(f"Screenshot saved to {args.screenshot}", file=sys.stderr)
            
            result = {
                "success": True,
                "output": content,
                "url": page.url,
                "title": page.title()
            }
            
        except Exception as e:
            result = {
                "success": False,
                "error": str(e)
            }
        finally:
            browser.close()
    
    # Output result
    if args.format == "json":
        output = json.dumps(result, ensure_ascii=False, indent=2)
    else:
        if result["success"]:
            output = result["output"]
        else:
            output = f"Error: {result['error']}"
    
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
