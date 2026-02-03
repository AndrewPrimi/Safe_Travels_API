"""Test script for google_maps_final.py

This script tests the final Google Maps helper function and saves
results to JSON for inspection.

Usage:
    python -m src.tests.test_google_maps_final
"""
import json
from datetime import datetime
from pathlib import Path

from src.helper_functions.google_maps_final import get_routes


def test_google_maps_final():
    """Test the final Google Maps helper and save results to JSON."""

    # Test addresses
    start = "Willis Tower, Chicago, IL"
    destination = "Navy Pier, Chicago, IL"

    print("=" * 60)
    print("Google Maps Final Helper - Test")
    print("=" * 60)
    print(f"\nStart: {start}")
    print(f"Destination: {destination}")
    print("\nCalling Google Maps API...")

    try:
        # Call the helper function
        routes = get_routes(
            start=start,
            destination=destination,
            include_traffic=True
        )

        print(f"\n[SUCCESS] Found {len(routes)} route(s)")

        # Create output data structure
        output_data = {
            "test_metadata": {
                "timestamp": datetime.now().isoformat(),
                "start_address": start,
                "destination_address": destination,
                "num_routes_found": len(routes)
            },
            "routes": routes
        }

        # Determine output file path
        tests_dir = Path(__file__).parent
        output_file = tests_dir / "google_maps_final_results.json"

        # Save to JSON file
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(f"\n[OK] Results saved to: {output_file}")

        # Print summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)

        for route in routes:
            print(f"\nRoute {route['route_id']}: {route['summary']}")
            print(f"  Distance: {route['distance_miles']} miles")
            print(f"  Duration: {route['duration_minutes']} minutes")
            print(f"  Waypoints: {len(route['waypoints'])}")

            if route['traffic']:
                print(f"  Traffic: {route['traffic']['traffic_condition']} "
                      f"(+{route['traffic']['traffic_delay_minutes']} min delay)")

            # Show first 3 waypoints
            print(f"\n  Sample waypoints:")
            for i, wp in enumerate(route['waypoints'][:3]):
                print(f"    {i+1}. ({wp['latitude']:.6f}, {wp['longitude']:.6f})")
            if len(route['waypoints']) > 3:
                print(f"    ... and {len(route['waypoints']) - 3} more waypoints")

        print("\n" + "=" * 60)
        print(f"[OK] Test completed successfully!")
        print(f"[OK] Full results available in: {output_file}")
        print("=" * 60)

        return output_data

    except ValueError as e:
        print(f"\n[ERROR] Error: {e}")
        print("\nPossible causes:")
        print("  - GOOGLE_MAPS_API_KEY not set in .env file")
        print("  - Invalid API key")
        print("  - Invalid addresses")
        return None

    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = test_google_maps_final()

    if result is None:
        print("\n[WARNING] Test failed - see errors above")
        exit(1)
    else:
        print("\n[OK] Test passed")
        exit(0)
