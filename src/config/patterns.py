import re

PRODUCT_PATTERNS = [
    re.compile(r'(.*/buy/*.*)'),
    re.compile(r'(.*-p[0-9]+\.(html).*)'),
    re.compile(r'(.*/(product)/.*)'),
    re.compile(r'(.*/(dp)/.*)'),
    re.compile(r'(.*/p/.*)'),
    re.compile(r'(.*(\/productpage)\.)\d+(\.html)')
]

PATTERNS_TO_IGNORE = [
    re.compile(r'(.*/(contact).*)'),
    re.compile(r'(.*/(about).*)'),
    re.compile(r'(.*/(help).*)'),
    re.compile(r'(.*/(faq).*)'),
    re.compile(r'(.*/(privacy).*)'),
    re.compile(r'(.*/(terms).*)'),
    re.compile(r'(.*/(shipping).*)'),
    re.compile(r'(.*/(log).*)'),
    re.compile(r'(.*/(forgot).*)'),
    re.compile(r'(.*/(cart).*)'),
    re.compile(r'(.*/(checkout).*)'),
    re.compile(r'(.*/(payment).*)'),
    re.compile(r'(.*/(order).*)'),
    re.compile(r'(.*/(return).*)'),
    re.compile(r'(.*/(track).*)'),
    re.compile(r'.*/(news).*'),
    re.compile(r'.*(customer).*'),
    re.compile(r'.*(privacy).*'),
    # Common files to ignore
    re.compile(r'.*/robots\.txt$'),
    re.compile(r'.*/sitemap\.xml$'),
    re.compile(r'.*/favicon\.ico$'),
    re.compile(r'.*/manifest\.json$'),
    re.compile(r'.*/ads\.txt$'),
    re.compile(r'.*/security\.txt$')
]
