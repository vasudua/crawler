# E-commerce Product Crawler

A high-performance, concurrent web crawler designed to extract product URLs from e-commerce websites. Built with Python, asyncio, and Playwright.

## Features

- **Concurrent Crawling**: Efficiently crawl multiple domains simultaneously
- **Smart URL Detection**: Automatically identify product pages using configurable patterns
- **Resource Management**: Proper cleanup of browser resources
- **Configurable Patterns**: Easy to customize product and ignore URL patterns
- **Result Persistence**: Automatically saves results to JSON

## Architecture

The crawler is built with a modular architecture:

```
src/
├── core/
│   ├── crawler.py     # Main crawler implementation
│   └── director.py    # Orchestrates multiple crawlers
├── utils/
│   └── url_utils.py   # URL manipulation utilities
└── config/
    └── patterns.py    # URL pattern definitions
```

### Components

1. **CrawlDirector** (`src/core/director.py`)
   - Manages concurrent crawling of multiple domains
   - Handles result aggregation and persistence
   - Uses ThreadPoolExecutor for parallelization

2. **Crawler** (`src/core/crawler.py`)
   - Handles single-domain crawling
   - Uses Playwright for browser automation
   - Implements infinite scroll handling
   - Manages concurrent URL processing

3. **URL Utilities** (`src/utils/url_utils.py`)
   - URL normalization and validation
   - Domain comparison
   - Pattern matching for product/ignore URLs

4. **Patterns** (`src/config/patterns.py`)
   - Regular expressions for product URL detection
   - Patterns for URLs to ignore
   - Easily extensible for different e-commerce platforms

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -e ".[test]"
```

3. Install Playwright browsers:
```bash
playwright install firefox
```

## Usage

```python
from core.director import CrawlDirector

# Initialize the director
director = CrawlDirector()

# Define domains to crawl
domains = ["example.com", "shop.example.org"]

# Execute crawlers and get results
results = director.execute_crawlers(domains)

# Results are also saved to results.json
```

## Configuration

### Product URL Patterns

Add or modify patterns in `src/config/patterns.py`:

```python
PRODUCT_PATTERNS = [
    re.compile(r'(.*/product/.*)'),  # Standard product path
    re.compile(r'(.*/p/.*)'),        # Short product paths
    # Add your patterns here
]
```

### URLs to Ignore

Configure in `src/config/patterns.py`:

```python
PATTERNS_TO_IGNORE = [
    re.compile(r'(.*/(about).*)'),   # About pages
    re.compile(r'(.*/(cart).*)'),    # Shopping cart
    # Add your patterns here
]
```

## Testing

Run the test suite:

```bash
pytest
```

The test suite includes:
- Unit tests for URL utilities
- Integration tests for crawler functionality
- Concurrent execution tests

## Development

### Adding New Features

1. URL Patterns:
   - Add new patterns to `PRODUCT_PATTERNS` or `PATTERNS_TO_IGNORE`
   - Use descriptive comments for pattern purpose
   - Test patterns with various URLs

2. Crawler Behavior:
   - Modify `Crawler.extract_urls()` for custom extraction logic
   - Update browser configuration in `Crawler.setup_browser()`
   - Handle new URL types in URL utilities

### Best Practices

- Add comprehensive docstrings to new functions
- Include examples in docstrings
- Add appropriate type hints
- Write tests for new functionality
- Follow existing code style (use YAPF for formatting)

## License

MIT License - feel free to use and modify as needed.
