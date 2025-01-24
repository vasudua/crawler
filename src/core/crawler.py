import asyncio
import logging
from typing import List
from playwright.async_api import async_playwright

from utils.url_utils import (normalize_domain, normalize_url, is_out_of_domain,
                             is_ignore_url, is_product_url)


class Crawler:

  def __init__(self, domain: str, max_concurrent_tasks: int = 50) -> None:
    self.domain: str = normalize_domain(domain)
    self.max_concurrent_tasks: int = max_concurrent_tasks
    self.base_url: str = f"https://{domain}"
    self.product_urls: set[str] = set()
    self.context = None
    self.crawl_queue: asyncio.Queue[str] = asyncio.Queue()
    self.visited_urls: set = set()

  async def setup_browser(self) -> None:
    self.playwright = await async_playwright().start()
    self.browser = await self.playwright.firefox.launch(headless=True)
    self.context = await self.browser.new_context(
        viewport={
            'width': 1920,
            'height': 1080
        },
        java_script_enabled=True,
        ignore_https_errors=True,
        extra_http_headers={
            'Accept':
            'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
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
    logging.info(f"Extracting URLs from {url_to_visit}")
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
          if is_product_url(link) and not is_out_of_domain(
              link, self.base_url):
            logging.info(f"Product URL: {link}")
            self.product_urls.add(link)
          elif link not in self.visited_urls and not is_out_of_domain(
              link, self.base_url) and not is_ignore_url(link):
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
      logging.error(f"Error crawling {self.domain}: {e}")

    return extracted_urls

  async def dequeue_and_visit(self):
    url_to_goto: str = await self.crawl_queue.get()
    url_to_goto = normalize_url(url_to_goto)
    if url_to_goto in self.visited_urls or is_out_of_domain(
        url_to_goto, self.base_url) or is_ignore_url(url_to_goto):
      self.crawl_queue.task_done()
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
          asyncio.create_task(self.dequeue_and_visit()) for _ in range(
              min(self.crawl_queue.qsize(), self.max_concurrent_tasks))
      ]
      await asyncio.gather(*tasks)

    return list(self.product_urls)
