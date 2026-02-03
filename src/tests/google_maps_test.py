"""Google Maps API Test - Save results to JSON

This script tests the Google Maps helper function with sample addresses
and saves the complete results to a JSON file for inspection.

Usage:
    python src/tests/google_maps_test.py

Requirements:
    - GOOGLE_MAPS_API_KEY must be set in .env file
"""
import json
import os
from datetime import datetime
from pathlib import Path

from src.helper_functions.google_maps import use_google_maps


def test_google_maps_api():
    """Test Google Maps API and save results to JSON."""

    # Test addresses
    start = "Willis Tower, Chicago, IL"
    destination = "Navy Pier, Chicago, IL"

    print("=" * 60)
    print("Google Maps API Test")
    print("=" * 60)
    print(f"\nStart: {start}")
    print(f"Destination: {destination}")
    print("\nCalling Google Maps API...")

    try:
        # Call the Google Maps helper function
        routes = use_google_maps(
            start=start,
            destination=destination,
            include_traffic=True,
            include_places=True,
            place_types=["gas_station", "police"]
        )

        print(f"\n[SUCCESS] Found {len(routes)} route(s)")

        # Convert routes to dictionaries for JSON serialization
        routes_data = [route.to_dict() for route in routes]

        # Create output data structure
        output_data = {
            "test_metadata": {
                "timestamp": datetime.now().isoformat(),
                "start_address": start,
                "destination_address": destination,
                "num_routes_found": len(routes)
            },
            "routes": routes_data
        }

        # Determine output file path
        tests_dir = Path(__file__).parent
        output_file = tests_dir / "google_maps_test_results.json"

        # Save to JSON file
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(f"\n[OK] Results saved to: {output_file}")

        # Print summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)

        for route in routes:
            print(f"\nRoute {route.route_id}: {route.summary}")
            print(f"  Distance: {route.distance_miles} miles")
            print(f"  Duration: {route.duration_minutes} minutes")
            print(f"  Waypoints: {len(route.waypoints)}")

            if route.traffic:
                print(f"  Traffic: {route.traffic.traffic_condition} "
                      f"(+{route.traffic.traffic_delay_minutes} min delay)")

            if route.places_along_route:
                print(f"  Places found: {len(route.places_along_route)}")
                for place in route.places_along_route[:3]:
                    print(f"    - {place.name} ({place.place_type})")
                if len(route.places_along_route) > 3:
                    print(f"    ... and {len(route.places_along_route) - 3} more")

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
    result = test_google_maps_api()

    if result is None:
        print("\n[WARNING] Test failed - see errors above")
        exit(1)
    else:
        print("\n[OK] Test passed")
        exit(0)
