import json
import logging
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio

from core.crawler import Crawler


class CrawlDirector:

  def execute_crawlers(self, domains: List[str]) -> Dict[str, List[str]]:
    """Execute registered crawlers for the given domains.
        
        Args:
            domains: List of domains to crawl
            
        Returns:
            Dictionary mapping domains to their crawled product URLs
        """

    async def execute_crawler(domain: str) -> List[str]:
      logging.info(f"Executing crawler for {domain}")
      crawler: Crawler = Crawler(domain)
      try:
        urls: List[str] = await crawler.crawl()
        return urls
      except Exception as e:
        logging.error(f"Error crawling {domain}: {e}")
        return []
      finally:
        await crawler.close_browser()

    results: Dict[str, List[str]] = {}
    with ThreadPoolExecutor(max_workers=50) as executor:
      futures_to_url = {
          executor.submit(asyncio.run, execute_crawler(domain)): domain
          for domain in domains
      }
      for future in as_completed(futures_to_url):
        domain = futures_to_url[future]
        try:
          results[domain] = future.result()
          logging.info(
              f"Crawled {domain} with {len(results[domain])} products")
        except Exception as e:
          logging.error(f"Error processing results for {domain}: {e}")
          results[domain] = []

    with open('results.json', 'w') as f:
      json.dump(results, f)
    return results
