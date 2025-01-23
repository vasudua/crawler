import asyncio
import json
import re
from dataclasses import dataclass
from typing import List
from urllib.parse import urlparse
from playwright.async_api import async_playwright
from concurrent.futures import ThreadPoolExecutor, as_completed

PRODUCT_PATTERNS = [
    re.compile(r'(.*/buy/*.*)'),
    re.compile(r'(.*-p[0-9]+\.(html).*)'),
    re.compile(r'(.*/(product)/.*)'),
    re.compile(r'(.*/(dp)/.*)'),
    re.compile(r'(.*/p/.*)'),
    re.compile(r'(.*(\/productpage)\.)\d+(\.html)')
]

PATTERNS_TO_IGNORE = [
  re.compile(r'(.*/(contact).*)'),
  re.compile(r'(.*/(about).*)'),
  re.compile(r'(.*/(help).*)'),
  re.compile(r'(.*/(faq).*)'),
  re.compile(r'(.*/(privacy).*)'),
  re.compile(r'(.*/(terms).*)'),
  re.compile(r'(.*/(shipping).*)'),
  re.compile(r'(.*/(log).*)'),
  re.compile(r'(.*/(forgot).*)'),
  re.compile(r'(.*/(cart).*)'),
  re.compile(r'(.*/(checkout).*)'),
  re.compile(r'(.*/(payment).*)'),
  re.compile(r'(.*/(order).*)'),
  re.compile(r'(.*/(return).*)'),
  re.compile(r'(.*/(track).*)'),
]


class Crawler:

  def __init__(self, domain: str, max_concurrent_tasks: int = 50) -> None:
    self.domain: str = self._normalize_domain(domain)
    self.max_concurrent_tasks: int = max_concurrent_tasks
    self.base_url: str = f"https://{domain}"
    self.product_urls: set[str] = set()
    self.context = None
    self.crawl_queue: asyncio.Queue[str] = asyncio.Queue()
    self.visited_urls: set = set()

  @staticmethod
  def _normalize_domain(domain: str) -> str:
    domain = domain.lower().strip()
    domain = re.sub(r'^https?://', '', domain)
    domain = re.sub(r'^www\.', '', domain)
    return domain

  async def setup_browser(self) -> None:
    self.playwright = await async_playwright().start()
    self.browser = await self.playwright.firefox.launch(headless=True)
    self.context = await self.browser.new_context(
      viewport={'width': 1920, 'height': 1080},
      java_script_enabled=True,
      ignore_https_errors=True,
      extra_http_headers={
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
          'Accept-Language': 'en-US,en;q=0.5',
          'Accept-Encoding': 'gzip, deflate, br',
          'DNT': '1',
          'Connection': 'keep-alive',
          'Upgrade-Insecure-Requests': '1'
      })

  async def close_browser(self) -> None:
    if self.browser:
      await self.browser.close()
    if self.playwright:
      await self.playwright.stop()

  async def extract_urls(self, url_to_visit: str) -> List[str]:
    extracted_urls: List[str] = []
    try:
      page = await self.context.new_page()

      # Start from the base URL
      await page.goto(url_to_visit, timeout=0)

      while True:
        # Extract product links
        links: List[str] = await page.eval_on_selector_all(
            "a[href]", "elements => elements.map(e => e.href)")

        for link in links:
          if self._is_product_url(link):
            print(f"Product URL: {link}")
            self.product_urls.add(link)
          elif link not in self.visited_urls and not self._is_out_of_domain(
            link) and not self._is_ignore_url(link):
            extracted_urls.append(link)

        # Try to scroll for infinite scrolling
        previous_height: int = await page.evaluate("document.body.scrollHeight"
                                                   )
        await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
        await asyncio.sleep(2)  # Wait for new content to load
        new_height: int = await page.evaluate("document.body.scrollHeight")
        if new_height == previous_height:
           break

      await page.close()
    except Exception as e:
      print(f"Error crawling {self.domain}: {e}")

    return extracted_urls

  def _is_product_url(self, url: str) -> bool:
    return any(re.search(pattern, url) for pattern in PRODUCT_PATTERNS)
  def _is_out_of_domain(self, url: str) -> bool:
    return urlparse(url).netloc.replace('www.', '') != urlparse(
        self.base_url).netloc.replace('www.', '')

  def _is_ignore_url(self, url: str) -> bool:
    return any(re.search(pattern, url) for pattern in PATTERNS_TO_IGNORE)

  async def dequeue_and_visit(self):
    url_to_goto: str = await self.crawl_queue.get()
    if url_to_goto in self.visited_urls or self._is_out_of_domain(
        url_to_goto) or self._is_ignore_url(url_to_goto):
      return
    extracted_urls: List[str] = await self.extract_urls(
        url_to_visit=url_to_goto)
    self.visited_urls.add(url_to_goto)
    for extracted_url in extracted_urls:
      await self.crawl_queue.put(extracted_url)
    self.crawl_queue.task_done()

  async def crawl(self) -> List[str]:
    if not self.context:
      await self.setup_browser()

    await self.crawl_queue.put(self.base_url)

    while not self.crawl_queue.empty():
      tasks = [
          asyncio.create_task(self.dequeue_and_visit())
          for _ in range(min(self.crawl_queue.qsize(), self.max_concurrent_tasks))
      ]
      await asyncio.gather(*tasks)

    return list(self.product_urls)


class CrawlDirector:

  def execute_crawlers(self, domains: List[str]) -> List[str]:
    """Execute registered crawlers for the given domains."""
    results: List[str] = []

    async def execute_crawler(domain: str) -> List[str]:
      print(f"Executing crawler for {domain}")

      crawler: Crawler = Crawler(domain)
      try:
        urls: List[str] = await crawler.crawl()
        results.extend(urls)
      finally:
        await crawler.close_browser()
      return urls

    results = {}
    with ThreadPoolExecutor(max_workers=50) as executor:
      futures_to_url = {
          executor.submit(asyncio.run, execute_crawler(domain)): domain
          for domain in domains
      }
      for future in as_completed(futures_to_url):
        domain = futures_to_url[future]
        results[domain] = future.result()
    with open('results.json', 'w') as f:
      json.dump(results, f)
    return results


def crawl(domains: List[str]) -> List[str]:
  director = CrawlDirector()
  return director.execute_crawlers(domains)


print(crawl(['www.zara.com/in', 'myntra.com', 'ajio.com', 'www2.hm.com/en_in']))
