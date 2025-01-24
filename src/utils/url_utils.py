import re
from urllib.parse import urlparse

from config.patterns import PRODUCT_PATTERNS, PATTERNS_TO_IGNORE


def normalize_domain(domain: str) -> str:
  domain = domain.lower().strip()
  domain = re.sub(r'^https?://', '', domain)
  domain = re.sub(r'^www\.', '', domain)
  return domain


def normalize_url(url: str) -> str:
  url = url.lower().strip()
  url = re.sub(r'#.*$', '', url)
  return url


def is_out_of_domain(url: str, base_url: str) -> bool:
  return urlparse(url).netloc.replace('www.',
                                      '') != urlparse(base_url).netloc.replace(
                                          'www.', '')


def is_product_url(url: str) -> bool:
  return any(re.search(pattern, url) for pattern in PRODUCT_PATTERNS)


def is_ignore_url(url: str) -> bool:
  return any(re.search(pattern, url) for pattern in PATTERNS_TO_IGNORE)
