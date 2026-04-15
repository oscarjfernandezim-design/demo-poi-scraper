"""
Data processing pipeline - handles deduplication, validation, and aggregation
Generator-based for low memory usage
"""

from typing import List, AsyncGenerator, Set
from models import POI
import json


class DataProcessor:
    """Process and validate POI data with deduplication"""

    def __init__(self):
        self.seen_pois: Set[str] = set()
        self.processed_count = 0

    def _create_poi_key(self, poi: POI) -> str:
        """Create unique key for deduplication"""
        return f"{poi.latitude:.4f}_{poi.longitude:.4f}_{poi.name}"

    async def deduplicate_and_validate(
        self,
        pois_generator: AsyncGenerator[POI, None]
    ) -> AsyncGenerator[POI, None]:
        """
        Async generator: deduplicate and validate POIs on-the-fly
        Yields only unique, valid POIs (memory efficient)
        """
        async for poi in pois_generator:
            key = self._create_poi_key(poi)

            # Skip duplicates
            if key in self.seen_pois:
                continue

            # Skip invalid entries
            if not poi.name or poi.latitude == 0 or poi.longitude == 0:
                continue

            self.seen_pois.add(key)
            self.processed_count += 1
            yield poi

    @staticmethod
    def aggregate_pois(pois: List[POI]) -> dict:
        """Aggregate POIs by type"""
        aggregated = {}

        for poi in pois:
            poi_type = poi.poi_type
            if poi_type not in aggregated:
                aggregated[poi_type] = []
            aggregated[poi_type].append(poi.to_dict())

        return aggregated

    @staticmethod
    def calculate_statistics(pois: List[POI]) -> dict:
        """Calculate dataset statistics"""
        if not pois:
            return {}

        sizes = [poi.size_kb() for poi in pois]
        total_size_kb = sum(sizes)

        return {
            "total_pois": len(pois),
            "unique_types": len(set(p.poi_type for p in pois)),
            "total_size_kb": round(total_size_kb, 4),
            "average_kb_per_record": round(total_size_kb / len(pois), 4),
            "max_record_kb": round(max(sizes), 4),
            "min_record_kb": round(min(sizes), 4),
            "types_breakdown": {
                poi_type: len([p for p in pois if p.poi_type == poi_type])
                for poi_type in set(p.poi_type for p in pois)
            }
        }

    @staticmethod
    def validate_poi(poi: POI) -> bool:
        """Validate POI data integrity"""
        return (
            poi.name and
            len(poi.name) > 0 and
            -90 <= poi.latitude <= 90 and
            -180 <= poi.longitude <= 180 and
            0 <= poi.confidence <= 1.0
        )
