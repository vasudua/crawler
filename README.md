# E-commerce Product Crawler

A high-performance, concurrent web crawler designed to extract product URLs from e-commerce websites. Built with Python, asyncio, and Playwright.

## Quick Start

### Prerequisites
- Python 3.9 or higher
- Make

### One-Command Setup
```bash
make setup
```
This will:
- Create a virtual environment
- Install all dependencies
- Set up Playwright browser
- Configure development tools

### Running

```bash
# Run the crawler
make run

# Run tests
make test

# Format code
make format
```

## Project Structure
```
src/
├── core/                   # Core crawler functionality
│   ├── crawler.py         # Main crawler implementation
│   └── director.py        # Multi-domain orchestration
├── utils/                 # Utility functions
│   └── url_utils.py       # URL processing utilities
└── config/               # Configuration
    └── patterns.py       # URL pattern definitions
```

## Usage Example

```python
from core.director import CrawlDirector

# Initialize and run
director = CrawlDirector()
results = director.execute_crawlers(["example.com"])

# Results are saved to results.json
```

## Development

### Available Commands
```bash
make help                    # Show all available commands
make check                   # Run all checks (tests and linting)
make dev-clean              # Clean all generated files
make dev-setup              # Setup development environment
```

### Configuration

Edit patterns in `src/config/patterns.py`:
```python
# Add product URL patterns
PRODUCT_PATTERNS = [
    re.compile(r'(.*/product/.*)'),  # Standard product path
    re.compile(r'(.*/p/.*)'),        # Short product paths
]

# Add URLs to ignore
PATTERNS_TO_IGNORE = [
    re.compile(r'(.*/(about).*)'),   # About pages
    re.compile(r'(.*/(cart).*)'),    # Shopping cart
]
```

## Features
- Concurrent crawling of multiple domains
- Smart product URL detection
- Configurable URL patterns
- Automatic result saving

## License
MIT License 