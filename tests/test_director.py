import pytest
import json
import os
from unittest.mock import patch, AsyncMock, MagicMock
from src.core.director import CrawlDirector
from src.core.crawler import Crawler


@pytest.fixture
def director():
  return CrawlDirector()


@pytest.fixture
def mock_crawler():
  crawler = AsyncMock(spec=Crawler)
  crawler.crawl.return_value = ["https://example.com/product/1"]
  crawler.close_browser = AsyncMock()
  return crawler


def test_director_initialization(director):
  assert isinstance(director, CrawlDirector)


@pytest.mark.asyncio
async def test_execute_crawler_single_domain(director, mock_crawler):
  domain = "example.com"
  expected_urls = ["https://example.com/product/1"]

  with patch('src.core.director.Crawler', return_value=mock_crawler):
    results = director.execute_crawlers([domain])

    assert domain in results
    assert results[domain] == expected_urls
    mock_crawler.crawl.assert_called_once()
    mock_crawler.close_browser.assert_called_once()


@pytest.mark.asyncio
async def test_execute_crawler_multiple_domains(director, mock_crawler):
  domains = ["example1.com", "example2.com"]

  with patch('src.core.director.Crawler', return_value=mock_crawler):
    results = director.execute_crawlers(domains)

    assert len(results) == 2
    for domain in domains:
      assert domain in results
      assert results[domain] == ["https://example.com/product/1"]

    assert mock_crawler.crawl.call_count == 2
    assert mock_crawler.close_browser.call_count == 2


@pytest.mark.asyncio
async def test_execute_crawler_with_error(director):
  domain = "error.com"
  error_crawler = AsyncMock(spec=Crawler)
  error_crawler.crawl.side_effect = Exception("Test error")
  error_crawler.close_browser = AsyncMock()

  with patch('src.core.director.Crawler', return_value=error_crawler):
    results = director.execute_crawlers([domain])

    assert domain in results
    assert results[domain] == []  # Empty list for failed crawl
    error_crawler.close_browser.assert_called_once()


def test_results_file_creation(director, mock_crawler, tmp_path):
  domain = "example.com"
  expected_urls = ["https://example.com/product/1"]

  # Change to temporary directory for test
  original_dir = os.getcwd()
  os.chdir(tmp_path)

  try:
    with patch('src.core.director.Crawler', return_value=mock_crawler):
      director.execute_crawlers([domain])

      # Check if results file was created
      assert os.path.exists('results.json')

      # Verify file contents
      with open('results.json', 'r') as f:
        results = json.load(f)
        assert domain in results
        assert results[domain] == expected_urls
  finally:
    # Clean up - change back to original directory
    os.chdir(original_dir)
