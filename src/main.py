from typing import Dict, List

from config.logging_config import setup_logging
from core.director import CrawlDirector


def crawl(domains: List[str]) -> Dict[str, List[str]]:
  setup_logging()
  director = CrawlDirector()
  return director.execute_crawlers(domains)


if __name__ == "__main__":
  domains = ['www.zara.com/in', 'myntra.com', 'ajio.com', 'www2.hm.com/en_in']
  results = crawl(domains)
  print(results)
