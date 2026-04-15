"""
Live demo: Testing Overpass API with NYC data
Comparing all sources side-by-side
"""

import asyncio
import json
from alternatives import OverpassScraper, print_comparison

# Same NYC bbox from main demo
NYC_BBOX = {
    "north": 40.7489,
    "south": 40.7380,
    "east": -73.9680,
    "west": -73.9789
}


async def demo_overpass():
    """Test Overpass API"""
    print("\n" + "="*80)
    print("TESTING OVERPASS API - POI EXTRACTION DEMO (NYC)")
    print("="*80)

    # Test different POI types
    poi_types = ["restaurant", "cafe", "library", "pharmacy", "bank"]

    all_results = {}
    total_pois = 0
    start_time = asyncio.get_event_loop().time()

    for poi_type in poi_types:
        print(f"\nquerying: {poi_type}...", end=" ", flush=True)

        results = await OverpassScraper.search_pois(NYC_BBOX, poi_type, limit=10)

        all_results[poi_type] = results
        total_pois += len(results)

        print(f"got {len(results)} results")

        # Show first result
        if results:
            first = results[0]
            kb = OverpassScraper.estimate_size_kb(first)
            print(f"  example: {first.get('name', 'Unknown')} @ ({first['lat']:.4f}, {first['lon']:.4f}) - {kb:.3f} KB")

    end_time = asyncio.get_event_loop().time()
    duration = end_time - start_time

    # Summary
    print("\n" + "="*80)
    print(f"\nresults summary - {total_pois} POIs collected in {duration:.2f}s")
    print("\nbreakdown by type:")
    for poi_type, results in all_results.items():
        print(f"  {poi_type:<12} {len(results)} results")

    # Calculate average KB
    total_kb = 0
    record_count = 0
    for results in all_results.values():
        for poi in results:
            total_kb += OverpassScraper.estimate_size_kb(poi)
            record_count += 1

    avg_kb = total_kb / record_count if record_count > 0 else 0

    print(f"\nperformance metrics:")
    print(f"  total payload: {total_kb:.2f} KB")
    print(f"  avg per record: {avg_kb:.3f} KB")
    print(f"  requests/sec: {len(poi_types) / duration:.2f}")

    # Show sample data
    if all_results.get("restaurant"):
        print(f"\nsample data (first restaurant):")
        sample = all_results["restaurant"][0]
        print(json.dumps(sample, indent=2))

    print("\n" + "="*80)


async def main():
    """Run all demos"""

    # Show comparison table
    print_comparison()

    # Run Overpass demo
    try:
        await demo_overpass()
    except Exception as e:
        print(f"error running Overpass demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
