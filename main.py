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
    print("\nstarting scraper - NYC bbox, 5 categories, target 100 POIs\n")

    start_time = time.time()
    all_pois: List[POI] = []

    # Initialize scraper with async context
    async with POIScraper() as scraper:
        scraper.stats["start_time"] = start_time

        processor = DataProcessor()

        # Search for POIs across multiple terms
        for search_term in DEMO_SEARCH_TERMS:
            # Create generator from scraper
            poi_generator = scraper.search_pois(
                query=search_term,
                bbox=DEMO_BBOX,
                limit=20
            )

            # Process with deduplication in real-time
            count = 0
            async for poi in processor.deduplicate_and_validate(poi_generator):
                all_pois.append(poi)
                count += 1

                # Stop if we reach target
                if len(all_pois) >= DEMO_RECORD_COUNT:
                    break

            # Print result for this category
            print(f"{search_term:<12} {count} result{'s' if count != 1 else ''}")

            if len(all_pois) >= DEMO_RECORD_COUNT:
                break

        scraper.stats["end_time"] = time.time()

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

    csv_file = output_mgr.export_csv(
        all_pois,
        filename="pois_demo.csv"
    )

    # Print comprehensive report
    output_mgr.print_report(all_pois, stats, scraper_stats)

    return all_pois, stats, scraper_stats


def main():
    """Entry point"""
    try:
        # Run async demo
        pois, stats, scraper_stats = asyncio.run(run_scraper_demo())

    except KeyboardInterrupt:
        print("\ninterrupted by user")
    except Exception as e:
        print(f"\nerror: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
