import re

# Patterns to identify product URLs across different e-commerce platforms
# Each pattern matches a common URL structure used for product pages
PRODUCT_PATTERNS = [
    re.compile(r'(.*/buy/*.*)'),  # Generic buy pages
    re.compile(r'(.*-p[0-9]+\.(html).*)'),  # Product pages with numeric IDs
    re.compile(r'(.*/(product)/.*)'),  # Standard product path
    re.compile(r'(.*/(dp)/.*)'),  # Amazon-style product pages
    re.compile(r'(.*/p/.*)'),  # Short product paths
    re.compile(r'(.*(\/productpage)\.)\d+(\.html)'
               )  # Product pages with numeric suffixes
]

# Patterns for URLs that should be ignored during crawling
# These typically include utility pages, user account pages, and common web files
PATTERNS_TO_IGNORE = [
    # Common website sections
    re.compile(r'(.*/(contact).*)'),  # Contact pages
    re.compile(r'(.*/(about).*)'),  # About pages
    re.compile(r'(.*/(help).*)'),  # Help/Support pages
    re.compile(r'(.*/(faq).*)'),  # FAQ pages
    re.compile(r'(.*/(privacy).*)'),  # Privacy policy
    re.compile(r'(.*/(terms).*)'),  # Terms of service
    re.compile(r'(.*/(shipping).*)'),  # Shipping information

    # User account related
    re.compile(r'(.*/(log).*)'),  # Login/Logout pages
    re.compile(r'(.*/(forgot).*)'),  # Password reset

    # Shopping process
    re.compile(r'(.*/(cart).*)'),  # Shopping cart
    re.compile(r'(.*/(checkout).*)'),  # Checkout process
    re.compile(r'(.*/(payment).*)'),  # Payment pages
    re.compile(r'(.*/(order).*)'),  # Order tracking
    re.compile(r'(.*/(return).*)'),  # Returns process
    re.compile(r'(.*/(track).*)'),  # Order tracking

    # Content sections
    re.compile(r'.*/(news).*'),  # News/Blog sections
    re.compile(r'.*(customer).*'),  # Customer service
    re.compile(r'.*(privacy).*'),  # Privacy related pages

    # Common web files
    re.compile(r'.*/robots\.txt$'),  # Robots.txt
    re.compile(r'.*/sitemap\.xml$'),  # Sitemap
    re.compile(r'.*/favicon\.ico$'),  # Favicon
    re.compile(r'.*/manifest\.json$'),  # Web app manifest
    re.compile(r'.*/ads\.txt$'),  # Ads.txt
    re.compile(r'.*/security\.txt$')  # Security.txt
]
