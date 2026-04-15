"""
High-performance async POI scraper
Uses Nominatim API for demo (legally safe)
"""

import httpx
import asyncio
import json
from typing import List, AsyncGenerator
import time
from datetime import datetime
from config import (
    REQUEST_TIMEOUT,
    MAX_RETRIES,
    RETRY_DELAY,
    MAX_CONCURRENT_REQUESTS,
    MIN_DELAY_BETWEEN_REQUESTS,
    NOMINATIM_BASE_URL,
    USER_AGENT
)
from models import POI, Address, Building


class POIScraper:
    """High-performance async scraper with rate limiting and retry logic"""

    def __init__(self):
        self.session = None
        self.rate_limiter = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
        self.last_request_time = 0
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "start_time": None,
            "end_time": None,
            "total_data_kb": 0
        }

    async def __aenter__(self):
        """Context manager entry"""
        limits = httpx.Limits(
            max_keepalive_connections=5,
            max_connections=10
        )
        self.session = httpx.AsyncClient(
            limits=limits,
            timeout=REQUEST_TIMEOUT,
            headers={"User-Agent": USER_AGENT}
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.session:
            await self.session.aclose()

    async def _rate_limit(self):
        """Enforce rate limiting between requests"""
        elapsed = time.time() - self.last_request_time
        if elapsed < MIN_DELAY_BETWEEN_REQUESTS:
            await asyncio.sleep(MIN_DELAY_BETWEEN_REQUESTS - elapsed)
        self.last_request_time = time.time()

    async def _request_with_retry(self, url: str, params: dict) -> dict:
        """Make HTTP request with exponential backoff retry"""
        async with self.rate_limiter:
            await self._rate_limit()

            for attempt in range(MAX_RETRIES):
                try:
                    self.stats["total_requests"] += 1
                    response = await self.session.get(url, params=params)
                    response.raise_for_status()
                    self.stats["successful_requests"] += 1
                    return response.json() if response.text else {}

                except httpx.HTTPError as e:
                    self.stats["failed_requests"] += 1
                    if attempt < MAX_RETRIES - 1:
                        wait_time = RETRY_DELAY * (2 ** attempt)
                        print(f"[WARN] Request failed (attempt {attempt + 1}), retrying in {wait_time}s...")
                        await asyncio.sleep(wait_time)
                    else:
                        print(f"[ERROR] Request failed after {MAX_RETRIES} attempts: {e}")
                        return {}

    async def search_pois(self, query: str, bbox: dict = None, limit: int = 10) -> AsyncGenerator[POI, None]:
        """
        Search for POIs using Nominatim API with reverse geocoding
        Uses bounding box for geographic filtering
        """
        params = {
            "q": query,
            "format": "json",
            "limit": limit,
            "addressdetails": 1
        }

        if bbox:
            params["viewbox"] = f"{bbox['west']},{bbox['south']},{bbox['east']},{bbox['north']}"
            params["bounded"] = 1

        try:
            results = await self._request_with_retry(
                f"{NOMINATIM_BASE_URL}/search",
                params
            )

            if not results:
                print(f"[WARN] No results for query: {query}")
                return

            for result in results:
                poi = self._parse_nominatim_result(result, query)
                if poi:
                    self.stats["total_data_kb"] += poi.size_kb()
                    yield poi

        except Exception as e:
            print(f"[ERROR] Error searching POIs: {e}")

    async def get_address_details(self, lat: float, lon: float) -> Address:
        """Reverse geocoding to get detailed address"""
        params = {
            "lat": lat,
            "lon": lon,
            "format": "json",
            "addressdetails": 1
        }

        try:
            result = await self._request_with_retry(
                f"{NOMINATIM_BASE_URL}/reverse",
                params
            )

            if result and "address" in result:
                addr = result["address"]
                return Address(
                    street=addr.get("road") or addr.get("street"),
                    house_number=addr.get("house_number"),
                    city=addr.get("city") or addr.get("town") or addr.get("village"),
                    postcode=addr.get("postcode")
                )
        except Exception as e:
            print(f"[WARN] Error getting address for {lat},{lon}: {e}")

        return Address()

    def _parse_nominatim_result(self, result: dict, query: str) -> POI:
        """Extract minimal POI data from Nominatim response"""
        try:
            poi = POI(
                name=result.get("name", "Unknown"),
                poi_type=query,
                latitude=float(result.get("lat", 0)),
                longitude=float(result.get("lon", 0))
            )

            # Extract address component if available
            if "address" in result:
                addr = result["address"]
                poi.address = Address(
                    street=addr.get("road") or addr.get("street"),
                    house_number=addr.get("house_number"),
                    city=addr.get("city") or addr.get("town"),
                    postcode=addr.get("postcode")
                )

            # Building type if available
            if "type" in result:
                poi.building = Building(
                    name=result.get("name"),
                    building_type=result.get("type")
                )

            return poi
        except Exception as e:
            print(f"[WARN] Error parsing result: {e}")
            return None

    def get_stats(self) -> dict:
        """Get scraping statistics"""
        if self.stats["start_time"] and self.stats["end_time"]:
            duration = self.stats["end_time"] - self.stats["start_time"]
            avg_kb = (
                self.stats["total_data_kb"] / self.stats["successful_requests"]
                if self.stats["successful_requests"] > 0
                else 0
            )

            return {
                **self.stats,
                "duration_seconds": round(duration, 2),
                "requests_per_second": round(
                    self.stats["successful_requests"] / duration if duration > 0 else 0,
                    2
                ),
                "average_kb_per_record": round(avg_kb, 4),
                "success_rate": round(
                    self.stats["successful_requests"] / self.stats["total_requests"] * 100
                    if self.stats["total_requests"] > 0
                    else 0,
                    1
                )
            }
        return self.stats
