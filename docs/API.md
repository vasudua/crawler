# API Documentation

## Core API

### CrawlDirector

```python
class CrawlDirector:
    def execute_crawlers(self, domains: List[str]) -> Dict[str, List[str]]:
        """
        Execute crawlers for multiple domains concurrently.
        
        Args:
            domains: List of domain names to crawl
            
        Returns:
            Dictionary mapping domains to their discovered product URLs
            
        Example:
            >>> director = CrawlDirector()
            >>> results = director.execute_crawlers(["example.com"])
            >>> print(results)
            {'example.com': ['https://example.com/product/1', ...]}
        """
```

### Crawler

```python
class Crawler:
    def __init__(self, domain: str, max_concurrent_tasks: int = 50):
        """
        Initialize a crawler for a specific domain.
        
        Args:
            domain: Domain to crawl
            max_concurrent_tasks: Maximum number of concurrent URL processing tasks
        """
    
    async def crawl(self) -> List[str]:
        """
        Start crawling the domain and collect product URLs.
        
        Returns:
            List of discovered product URLs
        """
    
    async def setup_browser(self) -> None:
        """
        Initialize the browser with optimal settings.
        """
    
    async def close_browser(self) -> None:
        """
        Clean up browser resources.
        """
```

## Utility Functions

### URL Processing

```python
def normalize_domain(domain: str) -> str:
    """
    Normalize a domain name.
    
    Args:
        domain: Domain name to normalize
        
    Returns:
        Normalized domain name
        
    Example:
        >>> normalize_domain("https://www.Example.com")
        'example.com'
    """

def normalize_url(url: str) -> str:
    """
    Normalize a URL.
    
    Args:
        url: URL to normalize
        
    Returns:
        Normalized URL
        
    Example:
        >>> normalize_url("https://example.com/path#fragment")
        'https://example.com/path'
    """

def is_out_of_domain(url: str, base_url: str) -> bool:
    """
    Check if URL is from a different domain.
    
    Args:
        url: URL to check
        base_url: Base URL to compare against
        
    Returns:
        True if URL is from different domain
        
    Example:
        >>> is_out_of_domain("https://other.com", "https://example.com")
        True
    """

def is_product_url(url: str) -> bool:
    """
    Check if URL is a product page.
    
    Args:
        url: URL to check
        
    Returns:
        True if URL is a product page
        
    Example:
        >>> is_product_url("https://example.com/product/123")
        True
    """

def is_ignore_url(url: str) -> bool:
    """
    Check if URL should be ignored.
    
    Args:
        url: URL to check
        
    Returns:
        True if URL should be ignored
        
    Example:
        >>> is_ignore_url("https://example.com/about")
        True
    """
```

## Configuration

### Product URL Patterns

```python
PRODUCT_PATTERNS: List[Pattern] = [
    re.compile(r'(.*/buy/*.*)'),         # Generic buy pages
    re.compile(r'(.*-p[0-9]+\.(html).*)'),  # Product pages with numeric IDs
    re.compile(r'(.*/(product)/.*)'),     # Standard product path
    re.compile(r'(.*/(dp)/.*)'),          # Amazon-style product pages
    re.compile(r'(.*/p/.*)'),             # Short product paths
]
```

### Ignore URL Patterns

```python
PATTERNS_TO_IGNORE: List[Pattern] = [
    # Common website sections
    re.compile(r'(.*/(contact).*)'),      # Contact pages
    re.compile(r'(.*/(about).*)'),        # About pages
    re.compile(r'(.*/(help).*)'),         # Help pages
    
    # User account related
    re.compile(r'(.*/(login).*)'),        # Login pages
    re.compile(r'(.*/(cart).*)'),         # Shopping cart
    
    # Common web files
    re.compile(r'.*/robots\.txt$'),       # Robots.txt
    re.compile(r'.*/sitemap\.xml$'),      # Sitemap
]
```

## Error Handling

The API uses Python's standard exception handling:

```python
try:
    director = CrawlDirector()
    results = director.execute_crawlers(["example.com"])
except Exception as e:
    logging.error(f"Crawling failed: {e}")
```

Common exceptions:
- `PlaywrightError`: Browser automation issues
- `NetworkError`: Connection problems
- `ValueError`: Invalid input parameters

## Logging

The system uses Python's standard logging:

```python
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Logs will include:
# - Crawler initialization
# - URL discovery
# - Error conditions
# - Completion status
```

## Result Format

The crawling results are saved in JSON format:

```json
{
    "example.com": [
        "https://example.com/product/1",
        "https://example.com/product/2"
    ],
    "shop.example.org": [
        "https://shop.example.org/p/item1"
    ]
}
``` 