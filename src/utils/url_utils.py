import re
from urllib.parse import urlparse

from config.patterns import PRODUCT_PATTERNS, PATTERNS_TO_IGNORE


def normalize_domain(domain: str) -> str:
  """
    Normalize a domain name by removing protocol, www prefix, and standardizing format.
    
    Args:
        domain: Domain name to normalize (e.g., "https://www.Example.com")
        
    Returns:
        Normalized domain name (e.g., "example.com")
        
    Examples:
        >>> normalize_domain("https://www.Example.com")
        'example.com'
        >>> normalize_domain("HTTP://Example.com")
        'example.com'
    """
  domain = domain.lower().strip()
  domain = re.sub(r'^https?://', '', domain)  # Remove protocol
  domain = re.sub(r'^www\.', '', domain)  # Remove www prefix
  return domain


def normalize_url(url: str) -> str:
  """
    Normalize a URL by removing fragments and standardizing format.
    
    Args:
        url: URL to normalize (e.g., "https://example.com/path#fragment")
        
    Returns:
        Normalized URL without fragments (e.g., "https://example.com/path")
        
    Examples:
        >>> normalize_url("https://example.com/path#fragment")
        'https://example.com/path'
        >>> normalize_url("  HTTPS://EXAMPLE.COM  ")
        'https://example.com'
    """
  url = url.lower().strip()
  url = re.sub(r'#.*$', '', url)  # Remove fragment
  return url


def is_out_of_domain(url: str, base_url: str) -> bool:
  """
    Check if a URL belongs to a different domain than the base URL.
    
    Args:
        url: URL to check
        base_url: Base URL to compare against
        
    Returns:
        True if URL is from a different domain, False otherwise
        
    Examples:
        >>> is_out_of_domain("https://other.com/path", "https://example.com")
        True
        >>> is_out_of_domain("https://www.example.com/path", "https://example.com")
        False
    """
  return urlparse(url).netloc.replace('www.',
                                      '') != urlparse(base_url).netloc.replace(
                                          'www.', '')


def is_product_url(url: str) -> bool:
  """
    Check if a URL is a product page based on predefined patterns.
    
    Args:
        url: URL to check
        
    Returns:
        True if URL matches any product patterns, False otherwise
        
    Examples:
        >>> is_product_url("https://example.com/product/123")
        True
        >>> is_product_url("https://example.com/about")
        False
    """
  return any(re.search(pattern, url) for pattern in PRODUCT_PATTERNS)


def is_ignore_url(url: str) -> bool:
  """
    Check if a URL should be ignored based on predefined patterns.
    
    Args:
        url: URL to check
        
    Returns:
        True if URL should be ignored, False otherwise
        
    Examples:
        >>> is_ignore_url("https://example.com/about")
        True
        >>> is_ignore_url("https://example.com/product/123")
        False
    """
  return any(re.search(pattern, url) for pattern in PATTERNS_TO_IGNORE)
