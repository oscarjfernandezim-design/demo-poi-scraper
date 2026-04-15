"""
Alternative data sources for POI extraction
Comparing: Nominatim, Overpass API, and Foursquare
"""

import httpx
import asyncio
import json
from typing import List, Dict
import time

# ============================================================================
# 1. OVERPASS API (OpenStreetMap) - FREE & LEGAL
# ============================================================================

class OverpassScraper:
    """
    Overpass API: Free query engine for OpenStreetMap data
    - No API key required
    - Completely legal and unrestricted
    - Excellent for POIs in any region
    - Perfect for large-scale extractions
    """

    BASE_URL = "https://overpass-api.de/api/interpreter"

    @staticmethod
    async def search_pois(bbox: dict, poi_type: str, limit: int = 50) -> List[Dict]:
        """
        Query Overpass API using bbox and POI type
        Format: (south, west, north, east)
        """
        # Map common POI types to OpenStreetMap tags
        osm_tag_map = {
            "restaurant": "amenity=restaurant",
            "cafe": "amenity=cafe",
            "library": "amenity=library",
            "pharmacy": "amenity=pharmacy",
            "bank": "amenity=bank"
        }

        osm_tag = osm_tag_map.get(poi_type, f"name=*")

        # Overpass QL query - correct syntax
        query = f"""[out:json];
(node[{osm_tag}]({bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']});
way[{osm_tag}]({bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']});
);
out center;"""

        async with httpx.AsyncClient(timeout=30) as client:
            try:
                response = await client.post(
                    OverpassScraper.BASE_URL,
                    data={"data": query}
                )
                response.raise_for_status()
                data = response.json()

                pois = []
                for element in data.get("elements", []):
                    if "tags" in element and "name" in element["tags"]:
                        lat = element.get("lat")
                        lon = element.get("lon")
                        if not lat:
                            lat = element.get("center", {}).get("lat")
                        if not lon:
                            lon = element.get("center", {}).get("lon")

                        if lat and lon:
                            poi = {
                                "name": element["tags"].get("name", "Unknown"),
                                "type": poi_type,
                                "lat": lat,
                                "lon": lon,
                                "address": element["tags"].get("address", ""),
                            }
                            pois.append(poi)

                return pois[:limit]
            except Exception as e:
                print(f"Error: {e}")
                return []

    @staticmethod
    def estimate_size_kb(poi: Dict) -> float:
        """Estimate size in KB"""
        return len(json.dumps(poi)) / 1024


# ============================================================================
# 2. FOURSQUARE API - FREEMIUM (Limited free tier)
# ============================================================================

class FoursquareScraper:
    """
    Foursquare API: Professional-grade venue database
    - Free tier: 99,999 calls/day
    - 50 results per query
    - Requires API Key + Access Token
    - Much better data quality than Nominatim
    """

    BASE_URL = "https://api.foursquare.com/v3"

    @staticmethod
    async def search_pois(
        bbox: dict,
        query: str,
        access_token: str,
        limit: int = 50
    ) -> List[Dict]:
        """Query Foursquare for venues"""

        # Foursquare uses ne, sw format
        ne = f"{bbox['north']},{bbox['east']}"
        sw = f"{bbox['south']},{bbox['west']}"

        params = {
            "query": query,
            "ne": ne,
            "sw": sw,
            "limit": min(limit, 50)
        }

        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {access_token}"
        }

        async with httpx.AsyncClient(timeout=30) as client:
            try:
                response = await client.get(
                    f"{FoursquareScraper.BASE_URL}/places/search",
                    params=params,
                    headers=headers
                )
                data = response.json()

                pois = []
                for result in data.get("results", []):
                    poi = {
                        "name": result.get("name"),
                        "type": query,
                        "lat": result["geocodes"]["main"]["latitude"],
                        "lon": result["geocodes"]["main"]["longitude"],
                        "address": result.get("location", {}).get("formatted_address"),
                        "categories": [c["name"] for c in result.get("categories", [])]
                    }
                    pois.append(poi)

                return pois
            except Exception as e:
                print(f"Error querying Foursquare: {e}")
                return []

    @staticmethod
    def estimate_size_kb(poi: Dict) -> float:
        """Estimate size in KB"""
        return len(json.dumps(poi)) / 1024


# ============================================================================
# COMPARACIÓN
# ============================================================================

COMPARISON = {
    "Nominatim (OpenStreetMap)": {
        "cost": "Free",
        "rate_limit": "1 req/sec",
        "accuracy": "Good (75%)",
        "address_quality": "Very Good",
        "legal": "Yes",
        "api_key": "No",
        "avg_kb_per_record": 0.26,
        "best_for": "General POI extraction, cost-sensitive projects"
    },
    "Overpass API (OpenStreetMap)": {
        "cost": "Free",
        "rate_limit": "Unlimited (but slow)",
        "accuracy": "Very Good (85%)",
        "address_quality": "Excellent",
        "legal": "Yes (100% compliant)",
        "api_key": "No",
        "avg_kb_per_record": 0.35,
        "best_for": "Large-scale free extractions, community data"
    },
    "Foursquare": {
        "cost": "$0 (99.9K calls/day free)",
        "rate_limit": "5000 per hour",
        "accuracy": "Excellent (95%)",
        "address_quality": "Excellent",
        "legal": "Yes (official API)",
        "api_key": "Yes (OAuth)",
        "avg_kb_per_record": 0.45,
        "best_for": "Professional use, high accuracy, business listings"
    },
    "HERE API": {
        "cost": "$0.40-$0.60 per 1000",
        "rate_limit": "High (depends on plan)",
        "accuracy": "Excellent (98%)",
        "address_quality": "Excellent",
        "legal": "Yes (official)",
        "api_key": "Yes",
        "avg_kb_per_record": 0.50,
        "best_for": "Enterprise, premium data quality"
    },
    "Google Maps API": {
        "cost": "$0.50-$7 per 1000",
        "rate_limit": "High (depends on plan)",
        "accuracy": "Best (99%)",
        "address_quality": "Best",
        "legal": "Yes (but most expensive)",
        "api_key": "Yes",
        "avg_kb_per_record": 0.55,
        "best_for": "When brand matters, heavy traffic"
    }
}


def print_comparison():
    """Print comparison table"""
    print("\n" + "="*120)
    print("POI DATA SOURCE COMPARISON")
    print("="*120)

    print(f"\n{'Source':<25} {'Cost':<20} {'Accuracy':<15} {'Legal':<10} {'API Key':<10} {'Avg KB':<10} {'Best For'}")
    print("-"*120)

    for source, data in COMPARISON.items():
        print(
            f"{source:<25} "
            f"{data['cost']:<20} "
            f"{data['accuracy']:<15} "
            f"{data['legal']:<10} "
            f"{data['api_key']:<10} "
            f"{data['avg_kb_per_record']:<10} "
            f"{data['best_for']}"
        )

    print("\n" + "="*120)
    print("\nRECOMMENDATION:")
    print("  - Development/Testing:    Overpass API (fastest, no auth)")
    print("  - Production Free Tier:    Foursquare (99.9K calls/day free)")
    print("  - Enterprise Cost-Optimal: HERE or TomTom")
    print("  - Brand Requirements:      Google Maps")
    print("="*120 + "\n")


if __name__ == "__main__":
    print_comparison()
