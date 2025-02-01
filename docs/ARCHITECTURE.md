# Architecture Documentation

## Overview

The crawler is designed with a focus on:
- Scalability through concurrent execution
- Resource efficiency
- Modularity and extensibility
- Robust error handling

## Core Components

### 1. CrawlDirector

The `CrawlDirector` class is the orchestrator that:
- Manages multiple crawler instances
- Handles concurrent execution
- Aggregates results
- Provides error isolation

Key design decisions:
- Uses `ThreadPoolExecutor` for parallel domain processing
- Implements async/await pattern for non-blocking operations
- Provides result persistence through JSON serialization

### 2. Crawler

The `Crawler` class handles single-domain crawling:
- Manages browser lifecycle
- Implements URL extraction logic
- Handles infinite scrolling
- Maintains visited URL tracking

Browser management:
- Uses Playwright for reliable automation
- Configures browser for optimal performance
- Ensures proper resource cleanup

URL processing:
- Concurrent URL queue processing
- Smart duplicate detection
- Domain-specific URL filtering

### 3. URL Utilities

The URL utilities provide:
- URL normalization
- Domain comparison
- Pattern matching

Design principles:
- Pure functions for testability
- Comprehensive validation
- Efficient regular expressions

### 4. Pattern Configuration

Pattern management:
- Centralized pattern definitions
- Easy customization
- Clear categorization

## Data Flow

1. Input Processing:
   ```
   Domains List → CrawlDirector → Individual Crawlers
   ```

2. URL Processing:
   ```
   Raw URLs → Normalization → Pattern Matching → Queue Management
   ```

3. Result Aggregation:
   ```
   Individual Results → Aggregation → JSON Storage
   ```

## Concurrency Model

The system uses a hybrid approach:
- Thread-level parallelism for domain processing
- Async/await for browser operations
- Queue-based URL processing

Benefits:
- Efficient resource utilization
- Scalable performance
- Controlled browser instances

## Error Handling

Multiple layers of error handling:
1. Browser-level errors
2. Network failures
3. Pattern matching issues
4. Concurrency-related errors

Strategy:
- Graceful degradation
- Comprehensive logging
- Resource cleanup
- Result preservation

## Extension Points

The system can be extended through:

1. Pattern Customization:
   - Add new product patterns
   - Modify ignore patterns
   - Implement custom pattern logic

2. Browser Configuration:
   - Customize browser settings
   - Add new browser types
   - Modify navigation behavior

3. Result Processing:
   - Implement custom storage
   - Add result transformation
   - Extend result format

## Performance Considerations

Key optimizations:
1. Concurrent domain processing
2. Efficient URL deduplication
3. Smart resource management
4. Configurable concurrency limits

Resource management:
- Browser instance lifecycle
- Memory usage control
- Network bandwidth optimization

## Testing Strategy

Multiple testing layers:
1. Unit tests for utilities
2. Integration tests for crawler
3. End-to-end tests for director
4. Performance benchmarks

Test coverage:
- URL processing
- Pattern matching
- Concurrency handling
- Error scenarios

## Future Improvements

Potential enhancements:
1. Distributed crawling using Celery in conjunction with Kafka/RabbitMQ & making it stateless.
2. Custom result processors
3. Advanced pattern matching
4. Performance monitoring
5. Rate limiting
6. Proxy support 
7. Cycle Detection
8. Geolocation based redirection
9. Persisting URLs in a Database