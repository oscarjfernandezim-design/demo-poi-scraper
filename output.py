"""
Output formatting - JSON and CSV export
"""

import json
import csv
import os
from typing import List, Dict
from datetime import datetime
from models import POI
from config import OUTPUT_PATH


class OutputManager:
    """Handle output generation in multiple formats"""

    def __init__(self):
        self.ensure_output_dir()

    @staticmethod
    def ensure_output_dir():
        """Create output directory if it doesn't exist"""
        if not os.path.exists(OUTPUT_PATH):
            os.makedirs(OUTPUT_PATH)

    @staticmethod
    def export_json(
        pois: List[POI],
        filename: str = None,
        statistics: dict = None,
        scraper_stats: dict = None
    ) -> str:
        """Export POIs to JSON with metadata"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pois_{timestamp}.json"

        filepath = os.path.join(OUTPUT_PATH, filename)

        output = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_records": len(pois),
                "format_version": "1.0"
            },
            "statistics": statistics or {},
            "scraper_performance": scraper_stats or {},
            "data": [poi.to_dict() for poi in pois]
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        return filepath

    @staticmethod
    def export_csv(
        pois: List[POI],
        filename: str = None
    ) -> str:
        """Export POIs to CSV format"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pois_{timestamp}.csv"

        filepath = os.path.join(OUTPUT_PATH, filename)

        if not pois:
            return filepath

        # Flatten POI data for CSV
        rows = []
        for poi in pois:
            row = {
                "name": poi.name,
                "type": poi.poi_type,
                "latitude": poi.latitude,
                "longitude": poi.longitude,
                "street": poi.address.street if poi.address else None,
                "house_number": poi.address.house_number if poi.address else None,
                "city": poi.address.city if poi.address else None,
                "postcode": poi.address.postcode if poi.address else None,
                "building_name": poi.building.name if poi.building else None,
                "building_type": poi.building.building_type if poi.building else None,
                "confidence": poi.confidence,
                "record_size_kb": poi.size_kb()
            }
            rows.append(row)

        fieldnames = list(rows[0].keys()) if rows else []

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        return filepath

    @staticmethod
    def print_report(
        pois: List[POI],
        statistics: dict = None,
        scraper_stats: dict = None
    ):
        """Print formatted report to console"""
        if not pois:
            print("no POIs collected")
            return

        print()

        # Query results summary
        if statistics and "types_breakdown" in statistics:
            types = statistics["types_breakdown"]
            print(f"scraping results - {len(pois)} POIs")
            for poi_type, count in types.items():
                # Pad the type name to align columns
                print(f"  {poi_type:<12} {count} result{'s' if count != 1 else ''}")

        # Performance metrics
        if scraper_stats:
            duration = scraper_stats.get("duration_seconds", 0)
            avg_kb = statistics.get("average_kb_per_record", 0) if statistics else 0
            print(f"\n{len(pois)} POIs collected in {duration}s - avg {avg_kb:.2f} KB/record")
            print(f"success rate: {scraper_stats.get('success_rate', 0):.0f}%")

        # File exports
        print(f"\noutput files:")
        print(f"  - ./output/pois_demo.json")
        print(f"  - ./output/pois_demo.csv")

        print()
