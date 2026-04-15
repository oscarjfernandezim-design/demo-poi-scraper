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
        print("\n" + "="*70)
        print("[REPORT] POI SCRAPER DEMO REPORT")
        print("="*70)

        # Data statistics
        if statistics:
            print("\n[DATA STATISTICS]:")
            print(f"  [OK] Total POIs: {statistics.get('total_pois', 0)}")
            print(f"  [OK] Unique Types: {statistics.get('unique_types', 0)}")
            print(f"  [OK] Total Size: {statistics.get('total_size_kb', 0)} KB")
            print(f"  [OK] Avg per Record: {statistics.get('average_kb_per_record', 0)} KB")
            print(f"  [OK] Min Record: {statistics.get('min_record_kb', 0)} KB")
            print(f"  [OK] Max Record: {statistics.get('max_record_kb', 0)} KB")

            if "types_breakdown" in statistics:
                print("\n  [BREAKDOWN]:")
                for poi_type, count in statistics["types_breakdown"].items():
                    print(f"    - {poi_type}: {count}")

        # Scraper performance
        if scraper_stats:
            print("\n[SCRAPER PERFORMANCE]:")
            print(f"  [OK] Total Requests: {scraper_stats.get('total_requests', 0)}")
            print(f"  [OK] Successful: {scraper_stats.get('successful_requests', 0)}")
            print(f"  [OK] Failed: {scraper_stats.get('failed_requests', 0)}")
            print(f"  [OK] Success Rate: {scraper_stats.get('success_rate', 0)}%")
            print(f"  [OK] Duration: {scraper_stats.get('duration_seconds', 0)}s")
            print(f"  [OK] Requests/sec: {scraper_stats.get('requests_per_second', 0)}")

        # Sample data
        if pois:
            print("\n[SAMPLE POIs]:")
            for i, poi in enumerate(pois[:5], 1):
                print(f"\n  {i}. {poi.name}")
                print(f"     Type: {poi.poi_type}")
                print(f"     Coords: ({poi.latitude:.4f}, {poi.longitude:.4f})")
                if poi.address:
                    addr = poi.address
                    addr_parts = [
                        addr.house_number,
                        addr.street,
                        addr.city,
                        addr.postcode
                    ]
                    addr_str = ", ".join([p for p in addr_parts if p])
                    if addr_str:
                        print(f"     Address: {addr_str}")
                print(f"     Size: {poi.size_kb()} KB")

        print("\n" + "="*70 + "\n")
