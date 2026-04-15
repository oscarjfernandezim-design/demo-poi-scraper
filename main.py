"""
Main entry point - Orchestrates the scraping pipeline
Production-ready demo showing efficient POI extraction
"""

import asyncio
import time
from typing import List
from scraper import POIScraper
from data_processor import DataProcessor
from output import OutputManager
from models import POI
from config import (
    DEMO_BBOX,
    DEMO_SEARCH_TERMS,
    DEMO_RECORD_COUNT,
    DEMO_OUTPUT_FILE
)


async def run_scraper_demo():
    """
    Main demo function:
    1. Searches for POIs across multiple categories
    2. Deduplicates and validates data
    3. Calculates statistics
    4. Exports to JSON/CSV
    5. Prints performance report
    """
    print("\n[START] Starting POI Scraper Demo...")
    print(f"[TARGET] {DEMO_RECORD_COUNT} POIs from {len(DEMO_SEARCH_TERMS)} categories")
    print(f"[REGION] NYC Bounding Box\n")

    start_time = time.time()
    all_pois: List[POI] = []

    # Initialize scraper with async context
    async with POIScraper() as scraper:
        scraper.stats["start_time"] = start_time

        processor = DataProcessor()

        # Search for POIs across multiple terms
        for search_term in DEMO_SEARCH_TERMS:
            print(f"[SEARCH] Searching for '{search_term}'...")

            # Create generator from scraper
            poi_generator = scraper.search_pois(
                query=search_term,
                bbox=DEMO_BBOX,
                limit=20
            )

            # Process with deduplication in real-time
            async for poi in processor.deduplicate_and_validate(poi_generator):
                all_pois.append(poi)
                print(f"   [OK] {poi.name} ({poi.poi_type}) - {poi.size_kb()} KB")

                # Stop if we reach target
                if len(all_pois) >= DEMO_RECORD_COUNT:
                    break

            if len(all_pois) >= DEMO_RECORD_COUNT:
                break

        scraper.stats["end_time"] = time.time()

    print(f"\n[SUCCESS] Scraping complete! Collected {len(all_pois)} unique POIs\n")

    # Calculate statistics
    stats = DataProcessor.calculate_statistics(all_pois)
    scraper_stats = scraper.get_stats()

    # Export output
    output_mgr = OutputManager()

    json_file = output_mgr.export_json(
        all_pois,
        filename=DEMO_OUTPUT_FILE,
        statistics=stats,
        scraper_stats=scraper_stats
    )
    print(f"[OUTPUT] JSON exported to: {json_file}")

    csv_file = output_mgr.export_csv(
        all_pois,
        filename="pois_demo.csv"
    )
    print(f"[OUTPUT] CSV exported to: {csv_file}")

    # Print comprehensive report
    output_mgr.print_report(all_pois, stats, scraper_stats)

    return all_pois, stats, scraper_stats


def main():
    """Entry point"""
    try:
        # Run async demo
        pois, stats, scraper_stats = asyncio.run(run_scraper_demo())

        print("[OK] Demo completed successfully!")
        print(f"\n[METRICS] Key Metrics:")
        print(f"   - Average record size: {stats.get('average_kb_per_record', 0)} KB")
        print(f"   - Success rate: {scraper_stats.get('success_rate', 0)}%")
        print(f"   - Processing speed: {scraper_stats.get('requests_per_second', 0)} req/s")

    except KeyboardInterrupt:
        print("\n[INTERRUPTED] Demo interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Error running demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
