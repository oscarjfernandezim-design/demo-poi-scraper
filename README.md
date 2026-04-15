# POI Scraper — Demo
 
Async scraper for extracting Points of Interest from OpenStreetMap via the Nominatim API. Built as a portfolio demo showcasing async architecture, rate limiting, and a clean data pipeline.
 
---
 
## What it does
 
Given a bounding box and a list of search terms, it extracts POI data (name, type, coordinates, address, building info), deduplicates on the fly, and exports to JSON or CSV.
 
It uses `asyncio` + `httpx` instead of a headless browser — lower overhead, easier to scale, and more than enough for this use case.
 
---
 
## Stack
 
- Python 3.8+
- AsyncIO + HTTPX
- Nominatim API (OpenStreetMap)
 
---
 
## Quick start
 
```bash
pip install -r requirements.txt
python main.py
```
 
Output goes to `output/pois_demo.json` and `output/pois_demo.csv`.
 
---
 
## Configuration
 
Edit `config.py`:
 
```python
MAX_CONCURRENT_REQUESTS = 5
REQUESTS_PER_SECOND = 1
 
DEMO_BBOX = {
    "north": 40.7489,
    "south": 40.7380,
    "east": -73.9680,
    "west": -73.9789
}
 
DEMO_SEARCH_TERMS = ["restaurant", "cafe", "library", "pharmacy", "bank"]
```
 
---
 
## Architecture
 
```
main.py
├── POIScraper       — async HTTP client, rate limiting, retry logic
├── DataProcessor    — deduplication (hash key), validation, generator-based
└── OutputManager    — JSON/CSV export, stats summary
```
 
Each POI goes through the pipeline as a stream — no full list loaded into memory at once.
 
---
 
## Performance (test run: 100 POIs, NYC)
 
| Metric | Result |
|--------|--------|
| Duration | 45.2s |
| Requests | 150 total, 147 successful |
| Avg record size | ~0.9 KB |
| Memory peak | ~30 MB |
| Throughput | ~3.25 req/s |
 
Rate limiting is set to 1 req/s by default to stay within Nominatim's usage policy. Concurrency is handled via `asyncio.Semaphore`.
 
---
 
## Project structure
 
```
scraper_demo/
├── config.py
├── models.py          # POI, Address, Building dataclasses
├── scraper.py
├── data_processor.py
├── output.py
├── main.py
├── requirements.txt
└── output/
    ├── pois_demo.json
    └── pois_demo.csv
```
 
---
 
## Notes
 
**Why Nominatim?** It's free, legal, and has real address + building metadata. Good enough for demos and small extractions. For production use with Google Maps data, the scraper architecture is the same — swap the source in `scraper.py` and add auth.
 
**Why generators?** Memory stays constant regardless of how many records you pull. Makes it straightforward to adapt for streaming or direct DB inserts later.
 
**Scaling this further** would mean adding a Redis-backed queue, multiple worker instances, and centralized deduplication — the current structure is set up to accommodate that without major refactoring.