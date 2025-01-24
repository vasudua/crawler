import json
import logging
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio

from core.crawler import Crawler


class CrawlDirector:
  """
    The CrawlDirector class orchestrates the crawling process across multiple domains.
    It manages concurrent crawling operations and handles result aggregation.
    """

  def execute_crawlers(self, domains: List[str]) -> Dict[str, List[str]]:
    """
        Execute crawlers for multiple domains concurrently.
        
        This method:
        1. Creates a crawler instance for each domain
        2. Runs crawlers concurrently using ThreadPoolExecutor
        3. Aggregates results from all crawlers
        4. Saves results to a JSON file
        
        Args:
            domains: List of domain names to crawl (e.g., ["example.com", "example.org"])
            
        Returns:
            Dictionary mapping domains to their discovered product URLs
            Example: {"example.com": ["https://example.com/product/1", ...]}
        """

    async def execute_crawler(domain: str) -> List[str]:
      """
            Execute a single crawler for a given domain.
            
            Args:
                domain: The domain to crawl
                
            Returns:
                List of discovered product URLs for the domain
            """
      logging.info(f"Executing crawler for {domain}")
      crawler: Crawler = Crawler(domain)
      try:
        urls: List[str] = await crawler.crawl()
        return urls
      except Exception as e:
        logging.error(f"Error crawling {domain}: {e}")
        return []
      finally:
        # Ensure browser resources are cleaned up even if crawling fails
        await crawler.close_browser()

    # Store results for each domain
    results: Dict[str, List[str]] = {}

    # Use ThreadPoolExecutor for concurrent execution
    with ThreadPoolExecutor(max_workers=50) as executor:
      # Create a mapping of futures to their corresponding domains
      futures_to_url = {
          executor.submit(asyncio.run, execute_crawler(domain)): domain
          for domain in domains
      }

      # Process completed futures as they finish
      for future in as_completed(futures_to_url):
        domain = futures_to_url[future]
        try:
          results[domain] = future.result()
          logging.info(
              f"Crawled {domain} with {len(results[domain])} products")
        except Exception as e:
          logging.error(f"Error processing results for {domain}: {e}")
          results[domain] = []

    # Save results to a JSON file for persistence
    with open('results.json', 'w') as f:
      json.dump(results, f)

    return results
