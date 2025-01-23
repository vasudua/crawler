import asyncio
import re
from dataclasses import dataclass
from typing import List
from urllib.parse import urlparse
from playwright.async_api import async_playwright
from concurrent.futures import ThreadPoolExecutor, as_completed

PATTERNS = [
    re.compile(r'(.*/buy/*.*)'),
    re.compile(r'(.*-p[0-9]+\.(html).*)'),
    re.compile(r'(.*/(product)/.*)'),
    re.compile(r'(.*/(shop)/.*)'),
    re.compile(r'(.*/(dp)/.*)'),
    re.compile(r'(.*/p/.*)'),
    re.compile(r'(.*(\/productpage)\.)\d+(\.html)')
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
    print(f"Extracting URLs from: {url_to_visit}")
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
          if any(re.search(pattern, link) for pattern in PATTERNS):
            self.product_urls.add(link)
          else:
            extracted_urls.append(link)

        print(f'Scrolling')
        # Try to scroll for infinite scrolling
        previous_height: int = await page.evaluate("document.body.scrollHeight"
                                                   )
        await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
        await asyncio.sleep(2)  # Wait for new content to load
        new_height: int = await page.evaluate("document.body.scrollHeight")
        if new_height == previous_height:
          print('Stop scolling')
          break

      await page.close()
    except Exception as e:
      print(f"Error crawling {self.domain}: {e}")

    return extracted_urls

  def _is_out_of_domain(self, url: str) -> bool:
    return urlparse(url).netloc.replace('www.', '') != urlparse(
        self.base_url).netloc.replace('www.', '')

  async def dequeue_and_visit(self):
    url_to_goto: str = await self.crawl_queue.get()
    if url_to_goto in self.visited_urls or self._is_out_of_domain(
        url_to_goto):
      print(f"Skipping URL: {url_to_goto}")
      return
    extracted_urls: List[str] = await self.extract_urls(
        url_to_visit=url_to_goto)
    self.visited_urls.add(url_to_goto)
    for extracted_url in extracted_urls:
      if extracted_url not in self.visited_urls and not self._is_out_of_domain(
          extracted_url):
        await self.crawl_queue.put(extracted_url)
    self.crawl_queue.task_done()

  async def crawl(self) -> List[str]:
    if not self.context:
      await self.setup_browser()

    await self.crawl_queue.put(self.base_url)

    while not self.crawl_queue.empty():
      print(
          f'URLs left to crawl: {self.crawl_queue.qsize()} for {self.base_url}'
      )
      print(
          f'Product URLs: {len(self.product_urls)}, Already visited: {len(self.visited_urls)}'
      )
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

    results = []
    with ThreadPoolExecutor(max_workers=50) as executor:
      futures = [
          executor.submit(asyncio.run, execute_crawler(domain))
          for domain in domains
      ]
      for future in as_completed(futures):
        results.extend(future.result())
    return results


def crawl(domains: List[str]) -> List[str]:
  director = CrawlDirector()
  return director.execute_crawlers(domains)


print(crawl(['zara.com/in', 'myntra.com']))
