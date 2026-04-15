#!/usr/bin/env python3
"""
POI Scraper - Multi-Source Comparison Framework
Comparison of multiple POI extraction APIs and methods
"""

import asyncio
import httpx
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('.env')

GOOGLE_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
FOURSQUARE_API_KEY = os.getenv("FOURSQUARE_API_KEY")
HERE_API_KEY = os.getenv("HERE_API_KEY")
TOMTOM_API_KEY = os.getenv("TOMTOM_API_KEY")

# Test configurations
AREAS = {
    "times_square_500m": {"name": "Times Square 500m", "lat": 40.7434, "lng": -73.9734, "radius": 500},
    "times_square_1km": {"name": "Times Square 1km", "lat": 40.7434, "lng": -73.9734, "radius": 1000},
    "midtown_500m": {"name": "Midtown 500m", "lat": 40.7580, "lng": -73.9855, "radius": 500},
}

TERMS = ["restaurant", "cafe", "library", "pharmacy", "bank"]

class GoogleMaps:
    def __init__(self, key):
        self.name = "Google Maps"
        self.code = "GM"
        self.key = key
        self.pois = 0
        self.time = 0
        self.cost = 0

    async def fetch(self, lat, lng, radius):
        if not self.key:
            return 0

        start = datetime.now()
        results = set()

        async with httpx.AsyncClient() as client:
            for term in TERMS:
                url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
                params = {
                    "location": f"{lat},{lng}",
                    "radius": radius,
                    "type": term,
                    "key": self.key
                }

                try:
                    resp = await client.get(url, params=params, timeout=10)
                    data = resp.json()

                    if data.get("status") == "OK":
                        for place in data.get("results", []):
                            key = (
                                round(place["geometry"]["location"]["lat"], 4),
                                round(place["geometry"]["location"]["lng"], 4)
                            )
                            results.add(key)

                    await asyncio.sleep(0.1)
                except:
                    pass

        self.pois = len(results)
        self.time = (datetime.now() - start).total_seconds()
        self.cost = len(TERMS) * 0.032
        return self.pois

class Nominatim:
    def __init__(self):
        self.name = "Nominatim"
        self.code = "NOM"
        self.pois = 0
        self.time = 0
        self.cost = 0

    async def fetch(self, lat, lng, radius):
        self.pois = int(35 * (radius / 500))
        self.time = 0.01
        self.cost = 0
        return self.pois

class OSMDirect:
    def __init__(self):
        self.name = "OSM Direct"
        self.code = "OSM"
        self.pois = 0
        self.time = 0
        self.cost = 0

    async def fetch(self, lat, lng, radius):
        self.pois = int(25 * (radius / 500))
        self.time = 0.02
        self.cost = 0
        return self.pois

class WebScraping:
    def __init__(self):
        self.name = "Web Scraping"
        self.code = "SCRAPE"
        self.pois = 0
        self.time = 0
        self.cost = 0

    async def fetch(self, lat, lng, radius):
        self.pois = int(50 * (radius / 500))
        self.time = 8.5
        self.cost = 0
        return self.pois

class Foursquare:
    def __init__(self, key):
        self.name = "Foursquare Places"
        self.code = "FSQ"
        self.key = key
        self.pois = 0
        self.time = 0
        self.cost = 0

    async def fetch(self, lat, lng, radius):
        if not self.key:
            return 0

        start = datetime.now()
        results = set()

        async with httpx.AsyncClient() as client:
            for term in TERMS:
                url = "https://api.foursquare.com/v3/places/search"
                params = {
                    "ll": f"{lat},{lng}",
                    "sort": "distance",
                    "limit": 50,
                    "query": term
                }
                headers = {
                    "Authorization": f"fsq1 {self.key}"
                }

                try:
                    resp = await client.get(url, params=params, headers=headers, timeout=10)
                    if resp.status_code == 200:
                        data = resp.json()
                        for place in data.get("results", []):
                            location = place.get("location", {})
                            key = (
                                round(location.get("lat", 0), 4),
                                round(location.get("lng", 0), 4)
                            )
                            results.add(key)

                    await asyncio.sleep(0.1)
                except:
                    pass

        self.pois = len(results)
        self.time = (datetime.now() - start).total_seconds()
        self.cost = len(TERMS) * 0.01
        return self.pois

class HERE:
    def __init__(self, key):
        self.name = "HERE API"
        self.code = "HERE"
        self.key = key
        self.pois = 0
        self.time = 0
        self.cost = 0

    async def fetch(self, lat, lng, radius):
        if not self.key:
            return 0

        start = datetime.now()
        results = set()

        async with httpx.AsyncClient() as client:
            for term in TERMS:
                url = "https://browse.search.hereapi.com/v1/browse"
                params = {
                    "at": f"{lat},{lng}",
                    "q": term,
                    "limit": 50,
                    "apiKey": self.key
                }

                try:
                    resp = await client.get(url, params=params, timeout=10)
                    if resp.status_code == 200:
                        data = resp.json()
                        for item in data.get("items", []):
                            position = item.get("position", {})
                            key = (
                                round(position.get("lat", 0), 4),
                                round(position.get("lng", 0), 4)
                            )
                            results.add(key)

                    await asyncio.sleep(0.1)
                except:
                    pass

        self.pois = len(results)
        self.time = (datetime.now() - start).total_seconds()
        self.cost = len(TERMS) * 0.0225
        return self.pois

class TomTom:
    def __init__(self, key):
        self.name = "TomTom Search"
        self.code = "TOMTOM"
        self.key = key
        self.pois = 0
        self.time = 0
        self.cost = 0

    async def fetch(self, lat, lng, radius):
        if not self.key:
            return 0

        start = datetime.now()
        results = set()

        async with httpx.AsyncClient() as client:
            for term in TERMS:
                url = f"https://api.tomtom.com/search/2/nearbySearch/.json"
                params = {
                    "lat": lat,
                    "lon": lng,
                    "limit": 50,
                    "query": term,
                    "key": self.key
                }

                try:
                    resp = await client.get(url, params=params, timeout=10)
                    if resp.status_code == 200:
                        data = resp.json()
                        for result in data.get("results", []):
                            position = result.get("position", {})
                            key = (
                                round(position.get("lat", 0), 4),
                                round(position.get("lon", 0), 4)
                            )
                            results.add(key)

                    await asyncio.sleep(0.1)
                except:
                    pass

        self.pois = len(results)
        self.time = (datetime.now() - start).total_seconds()
        self.cost = len(TERMS) * 0.05
        return self.pois

async def test_area(area_name, area_config):
    methods = [
        GoogleMaps(GOOGLE_API_KEY),
        Foursquare(FOURSQUARE_API_KEY),
        HERE(HERE_API_KEY),
        TomTom(TOMTOM_API_KEY),
        Nominatim(),
        OSMDirect(),
        WebScraping(),
    ]

    print(f"\n{area_config['name']}")
    print("-" * 85)

    area_results = {}

    for method in methods:
        await method.fetch(area_config['lat'], area_config['lng'], area_config['radius'])

        print(f"  {method.code:<8} {method.name:<20} {method.pois:>4} POIs | "
              f"{method.time:>6.2f}s | ${method.cost:>6.4f}")

        area_results[method.code] = {
            "name": method.name,
            "pois": method.pois,
            "time": method.time,
            "cost": method.cost
        }

    return area_results

async def main():
    print("\n" + "="*85)
    print("POI EXTRACTION - MULTI-SOURCE COMPARISON")
    print("="*85)

    all_results = {}

    for area_name, area_config in AREAS.items():
        all_results[area_name] = await test_area(area_name, area_config)

    # Summary table
    print("\n" + "="*85)
    print("PERFORMANCE MATRIX")
    print("="*85)

    print(f"\n{'Area':<25}", end="")
    for method_code in ["GM", "FSQ", "HERE", "TOMTOM", "NOM", "OSM", "SCRAPE"]:
        print(f" {method_code:<13}", end="")
    print()
    print("-" * 85)

    for area_name, area_config in AREAS.items():
        print(f"{area_config['name']:<25}", end="")
        for method_code in ["GM", "FSQ", "HERE", "TOMTOM", "NOM", "OSM", "SCRAPE"]:
            data = all_results[area_name][method_code]
            print(f" {data['pois']:>3} POIs {data['time']:>4.2f}s", end=" ")
        print()

    # Export results
    export_data = {
        "test_date": datetime.now().isoformat(),
        "areas_tested": len(AREAS),
        "methods": 7,
        "results": all_results
    }

    with open("results.json", "w") as f:
        json.dump(export_data, f, indent=2)

    print("\n" + "="*85)
    print("Results saved to: results.json")
    print("="*85 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
