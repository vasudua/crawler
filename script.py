import asyncio
import httpx
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from queue import Queue
from typing import List, Dict, Type, Optional, Any
from urllib.parse import urljoin
from playwright.async_api import async_playwright

PATTERNS = [
  re.compile(r'(.*/buy/*.*)'),
  re.compile(r'(.*-p[0-9]+\.(html).*)'),
]

class AsyncSet:
  def __init__(self):
    self._set = set()
    self._lock = asyncio.Lock()

  async def add(self, item):
    async with self._lock:
      self._set.add(item)

  async def remove(self, item):
    async with self._lock:
      self._set.remove(item)

  async def contains(self, item):
    async with self._lock:
      return item in self._set

@dataclass
class ExtractedURL:
  url: str
  parent: Optional[str]
  depth: int

# BaseCrawler class
class BaseCrawler(ABC):
  def __init__(self, domain: str) -> None:
    self.domain: str = domain
    self.base_url: str = f"https://{domain}"
    self.client: Optional[httpx.AsyncClient] = None
    self.product_urls: set[str] = set()

  async def init_client(self) -> None:
    self.client = httpx.AsyncClient()

  async def close_client(self) -> None:
    if self.client:
      await self.client.aclose()

  @abstractmethod
  async def crawl(self) -> List[str]:
    """Abstract method to crawl the domain for product URLs."""
    pass

  async def fetch_robots_txt(self) -> str:
    """Fetch and parse robots.txt to check for crawling permissions."""
    robots_url: str = urljoin(self.base_url, "/robots.txt")
    try:
      response = await self.client.get(robots_url)
      if response.status_code == 200:
        content: str = response.text
        return content
    except Exception as e:
      print(f"Failed to fetch robots.txt for {self.domain}: {e}")
    return ""

  def is_allowed_by_robots(self, robots_txt: str, user_agent: str = "*") -> bool:
    """Parse robots.txt to check if crawling is allowed."""
    lines: List[str] = robots_txt.splitlines()
    user_agent_match: bool = False
    for line in lines:
      line = line.strip()
      if line.lower().startswith("user-agent:"):
        user_agent_match = user_agent in line or "*" in line
      elif user_agent_match and line.lower().startswith("disallow:"):
        disallowed_path: str = line.split(":")[1].strip()
        if disallowed_path == "/" or disallowed_path == "":
          return False
    return True

# Example MyntraCrawler
class MyntraCrawler(BaseCrawler):
  async def extract_urls(self, url_to_visit: str, depth: int = 0) -> List[ExtractedURL]:
    extracted_urls: List[ExtractedURL] = []
    try:
      async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # Start from the base URL
        await page.goto(url_to_visit)

        while True:
          # Extract product links
          links: List[str] = await page.eval_on_selector_all(
            "a[href]",
            "elements => elements.map(e => e.href)"
          )

          for link in links:
            if any(re.search(pattern, link) for pattern in PATTERNS):
              self.product_urls.add(link)
            else:
              extracted_urls.append(ExtractedURL(url=link, parent=url_to_visit, depth=depth+1))

          print(f'Scrolling')
          # Try to scroll for infinite scrolling
          previous_height: int = await page.evaluate("document.body.scrollHeight")
          await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
          await asyncio.sleep(2)  # Wait for new content to load
          new_height: int = await page.evaluate("document.body.scrollHeight")
          if new_height == previous_height:
            break

        await browser.close()
    except Exception as e:
      print(f"Error crawling {self.domain}: {e}")

    return extracted_urls

  async def crawl(self) -> List[str]:
    """Crawl Zara's domain for product URLs."""
    if not self.client:
      await self.init_client()

    robots_txt: str = await self.fetch_robots_txt()
    if not self.is_allowed_by_robots(robots_txt):
      print(f"Crawling disallowed by robots.txt for {self.domain}")
      return []

    crawl_queue: Queue[ExtractedURL] = Queue()
    crawl_queue.put(ExtractedURL(url=self.base_url, parent=None, depth=0))

    visited_urls: set = set()
    while not crawl_queue.empty():
      url_to_goto: ExtractedURL = crawl_queue.get()
      print(f'URLs left to crawl: {crawl_queue.qsize()}')
      if url_to_goto.url in visited_urls:
        print(f"Skipping already visited URL: {url_to_goto.url}")
        continue
      extracted_urls: List[ExtractedURL] = await self.extract_urls(url_to_visit=url_to_goto.url, depth=url_to_goto.depth)
      print(f'Product URLs: {len(self.product_urls)}')
      visited_urls.add(url_to_goto.url)
      for extracted_url in extracted_urls:
        crawl_queue.put(extracted_url)

    return list(self.product_urls)

# CrawlDirector class
class CrawlDirector:
  def __init__(self) -> None:
    self.crawlers: Dict[str, Type[BaseCrawler]] = {}

  def register_crawler(self, domain: str, crawler_class: Type[BaseCrawler]) -> None:
    """Register a domain-specific crawler."""
    self.crawlers[domain] = crawler_class

  async def execute_crawlers(self, domains: List[str]) -> List[str]:
    """Execute registered crawlers for the given domains."""
    results: List[str] = []
    async def execute_crawler(domain: str) -> List[str]:
      print(f"Executing crawler for {domain}")
      crawler_class: Optional[Type[BaseCrawler]] = self.crawlers.get(domain)
      if not crawler_class:
        print(f"No crawler registered for {domain}")
        return []

      crawler: BaseCrawler = crawler_class(domain)
      await crawler.init_client()
      try:
        urls: List[str] = await crawler.crawl()
        results.extend(urls)
      finally:
        await crawler.close_client()
      return urls

    tasks = [execute_crawler(domain) for domain in domains]
    results = await asyncio.gather(*tasks)
    return results

def crawl_domains(domains: List[str]) -> Dict[str, Any]:
  crawl_director: CrawlDirector = CrawlDirector()
  crawl_director.register_crawler("zara.com/in", MyntraCrawler)
  crawl_director.register_crawler("myntra.com", MyntraCrawler)
  # Register more domain-specific crawlers as needed

  async def run_crawler() -> List[str]:
    return await crawl_director.execute_crawlers(domains)

  loop = asyncio.get_event_loop()
  urls: List[str] = loop.run_until_complete(run_crawler())

  # Save URLs to a file
  with open("product_urls.txt", "w") as f:
    f.writelines(f"{url}\n" for url in urls)

  return {"status": "completed", "total_urls": len(urls)}

# Example of scheduling the task
if __name__ == "__main__":
  result: Dict[str, Any] = crawl_domains(["zara.com/in", "myntra.com"])
  print(result)
  # print(f"Task ID: {result.id}")
