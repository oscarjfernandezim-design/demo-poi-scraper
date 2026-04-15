"""
Configuration for the scalable POI scraper
"""

# Request configuration
REQUEST_TIMEOUT = 10
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds

# Concurrency
MAX_CONCURRENT_REQUESTS = 5

# Rate limiting
REQUESTS_PER_SECOND = 1
MIN_DELAY_BETWEEN_REQUESTS = 1 / REQUESTS_PER_SECOND  # 1 second

# Data extraction
FIELDS_TO_EXTRACT = {
    "poi": ["name", "type", "lat", "lon"],
    "address": ["street", "house_number", "city", "postcode"],
    "building": ["name", "building_type"]
}

# Output configuration
OUTPUT_FORMAT = "json"  # json or csv
OUTPUT_PATH = "./output"
DEMO_OUTPUT_FILE = "pois_demo.json"

# Demo parameters
DEMO_BBOX = {
    "north": 40.7489,
    "south": 40.7380,
    "east": -73.9680,
    "west": -73.9789
}

DEMO_SEARCH_TERMS = [
    "restaurant",
    "cafe",
    "library",
    "pharmacy",
    "bank"
]

DEMO_RECORD_COUNT = 100

# Nominatim API
NOMINATIM_BASE_URL = "https://nominatim.openstreetmap.org"
USER_AGENT = "POI-Scraper-Demo/1.0"
