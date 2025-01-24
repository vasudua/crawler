import pytest
from src.utils.url_utils import (normalize_domain, normalize_url,
                                 is_out_of_domain, is_product_url,
                                 is_ignore_url)


@pytest.mark.parametrize("input_domain,expected", [
    ("example.com", "example.com"),
    ("http://example.com", "example.com"),
    ("https://example.com", "example.com"),
    ("www.example.com", "example.com"),
    ("https://www.example.com", "example.com"),
    ("EXAMPLE.com", "example.com"),
    ("  example.com  ", "example.com"),
    ("http://www.Example.Com", "example.com"),
])
def test_normalize_domain(input_domain, expected):
  assert normalize_domain(input_domain) == expected


@pytest.mark.parametrize("input_url,expected", [
    ("https://example.com", "https://example.com"),
    ("https://example.com#fragment", "https://example.com"),
    ("https://example.com#fragment/path", "https://example.com"),
    ("  https://example.com  ", "https://example.com"),
    ("HTTPS://EXAMPLE.COM", "https://example.com"),
])
def test_normalize_url(input_url, expected):
  assert normalize_url(input_url) == expected


@pytest.mark.parametrize("url,target_domain,expected", [
    ("https://example.com/product", "https://example.com", False),
    ("https://www.example.com/product", "https://example.com", False),
    ("https://example.com/product", "https://www.example.com", False),
    ("https://otherdomain.com/product", "https://example.com", True),
    ("https://subdomain.example.com", "https://example.com", True),
    ("https://example.org", "https://example.com", True),
])
def test_is_out_of_domain(url, target_domain, expected):
  assert is_out_of_domain(url, target_domain) == expected


@pytest.mark.parametrize("url,expected", [
    ("https://example.com/product/123", True),
    ("https://example.com/buy/item", True),
    ("https://example.com/category/item-p12345.html", True),
    ("https://example.com/dp/B00EXAMPLE", True),
    ("https://example.com/p/12345", True),
    ("https://example.com/productpage.12345.html", True),
    ("https://example.com/about", False),
    ("https://example.com/category", False),
    ("https://example.com", False),
])
def test_is_product_url(url, expected):
  assert is_product_url(url) == expected


@pytest.mark.parametrize("url,expected", [
    ("https://example.com/about", True),
    ("https://example.com/contact", True),
    ("https://example.com/help", True),
    ("https://example.com/faq", True),
    ("https://example.com/privacy", True),
    ("https://example.com/terms", True),
    ("https://example.com/shipping", True),
    ("https://example.com/login", True),
    ("https://example.com/cart", True),
    ("https://example.com/checkout", True),
    ("https://example.com/robots.txt", True),
    ("https://example.com/sitemap.xml", True),
    ("https://example.com/favicon.ico", True),
    ("https://example.com/product/123", False),
    ("https://example.com/category/shoes", False),
    ("https://example.com", False),
])
def test_is_ignore_url(url, expected):
  assert is_ignore_url(url) == expected


def test_normalize_domain_empty():
  assert normalize_domain("") == ""


def test_normalize_url_empty():
  assert normalize_url("") == ""


@pytest.mark.parametrize("invalid_input", [
    None,
    123,
    {},
    [],
])
def test_normalize_domain_invalid_input(invalid_input):
  with pytest.raises(AttributeError):
    normalize_domain(invalid_input)


@pytest.mark.parametrize("invalid_input", [
    None,
    123,
    {},
    [],
])
def test_normalize_url_invalid_input(invalid_input):
  with pytest.raises(AttributeError):
    normalize_url(invalid_input)
