import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from src.core.crawler import Crawler
from src.utils.url_utils import normalize_domain


@pytest.fixture
async def crawler():
  crawler = Crawler("example.com", max_concurrent_tasks=2)
  await crawler.setup_browser()
  yield crawler
  await crawler.close_browser()


@pytest.mark.asyncio
async def test_crawler_initialization():
  domain = "example.com"
  crawler = Crawler(domain)
  assert crawler.domain == normalize_domain(domain)
  assert crawler.base_url == f"https://{domain}"
  assert crawler.max_concurrent_tasks == 50
  assert isinstance(crawler.crawl_queue, asyncio.Queue)
  assert len(crawler.visited_urls) == 0
  assert len(crawler.product_urls) == 0


@pytest.mark.asyncio
async def test_browser_setup_and_close():
  crawler = Crawler("example.com")
  await crawler.setup_browser()
  assert crawler.browser is not None
  assert crawler.context is not None
  await crawler.close_browser()


@pytest.mark.asyncio
async def test_extract_urls(crawler):
  # Mock page and context for testing
  mock_page = AsyncMock()
  mock_page.eval_on_selector_all.return_value = [
      "https://example.com/product/1", "https://example.com/category",
      "https://example.com/product/2", "https://otherdomain.com/product/3"
  ]
  mock_page.evaluate.side_effect = [100, None, 100]  # For scroll height checks
  mock_page.goto = AsyncMock()
  mock_page.close = AsyncMock()

  with patch.object(crawler.context, 'new_page', return_value=mock_page):
    urls = await crawler.extract_urls("https://example.com")

    assert len(urls) == 1  # Only the category URL should be extracted
    assert "https://example.com/category" in urls
    assert len(crawler.product_urls
               ) == 2  # Only in-domain product URLs should be added
    assert "https://example.com/product/1" in crawler.product_urls
    assert "https://example.com/product/2" in crawler.product_urls


@pytest.mark.asyncio
async def test_crawl_basic_flow(crawler):
  # Mock extract_urls to return a controlled set of URLs
  with patch.object(crawler,
                    'extract_urls',
                    return_value=["https://example.com/page2"]):
    await crawler.crawl_queue.put(crawler.base_url)
    product_urls = await crawler.crawl()

    assert crawler.base_url in crawler.visited_urls
    assert "https://example.com/page2" in crawler.visited_urls
    assert isinstance(product_urls, list)


@pytest.mark.asyncio
async def test_dequeue_and_visit_with_invalid_urls(crawler):
  # Mock extract_urls to prevent actual URL extraction
  mock_extract = AsyncMock(return_value=[])

  with patch.object(crawler, 'extract_urls', mock_extract):
    # Test out of domain URL
    await crawler.crawl_queue.put("https://otherdomain.com")
    await crawler.dequeue_and_visit()
    assert "https://otherdomain.com" not in crawler.visited_urls
    assert not mock_extract.called

    # Test ignore URL
    await crawler.crawl_queue.put("https://example.com/robots.txt")
    await crawler.dequeue_and_visit()
    assert "https://example.com/robots.txt" not in crawler.visited_urls
    assert not mock_extract.called
