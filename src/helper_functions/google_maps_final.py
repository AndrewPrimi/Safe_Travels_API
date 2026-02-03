"""Google Maps Final Helper - SafeTravels API

Production-ready route helper for crime analysis.

Features:
- Multiple route alternatives
- Adaptive waypoint sampling (denser in urban areas, sparser on highways)
- Real-time traffic data
- Distance and duration calculations

Usage:
    from src.helper_functions.google_maps_final import get_routes

    routes = get_routes(
        start="Willis Tower, Chicago, IL",
        destination="Navy Pier, Chicago, IL"
    )

    # Access route data
    for route in routes:
        print(f"Route {route['route_id']}: {route['summary']}")
        print(f"Distance: {route['distance_miles']} miles")
        print(f"Waypoints: {len(route['waypoints'])}")
"""
import os
from typing import List, Dict, Any, Optional
import googlemaps
import polyline as polyline_lib
from math import radians, sin, cos, sqrt, atan2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Google Maps API key
GOOGLE_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two GPS coordinates in miles using Haversine formula.

    Args:
        lat1, lon1: First point coordinates
        lat2, lon2: Second point coordinates

    Returns:
        Distance in miles
    """
    R = 3959  # Earth's radius in miles

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))

    return R * c


def get_adaptive_interval(total_distance_miles: float) -> float:
    """
    Determine waypoint sampling interval based on route distance.

    Adaptive strategy:
    - Urban routes (< 5 mi): 0.5 mile intervals (very dense)
    - Short urban (5-10 mi): 0.75 mile intervals (dense)
    - Suburban (10-20 mi): 1.5 mile intervals (moderate)
    - Mixed (20-40 mi): 2.5 mile intervals
    - Highway (> 40 mi): 4 mile intervals (sparse)

    Args:
        total_distance_miles: Total route distance

    Returns:
        Sampling interval in miles
    """
    if total_distance_miles < 5:
        return 0.5   # Very dense for short urban routes
    elif total_distance_miles < 10:
        return 0.75  # Dense for urban routes
    elif total_distance_miles < 20:
        return 1.5   # Moderate for suburban
    elif total_distance_miles < 40:
        return 2.5   # Mixed urban/highway
    else:
        return 4.0   # Sparse for long highway routes


def sample_points_from_polyline(
    encoded_polyline: str,
    interval_miles: float
) -> List[Dict[str, Any]]:
    """
    Extract waypoints from a polyline at adaptive intervals.

    Ensures even distribution of waypoints along the route for
    comprehensive crime data coverage.

    Args:
        encoded_polyline: Google's encoded polyline string
        interval_miles: Distance between sample points

    Returns:
        List of waypoint dictionaries with latitude/longitude
    """
    # Decode the polyline to get all coordinate points
    coords = polyline_lib.decode(encoded_polyline)

    if not coords:
        return []

    # Always include start point
    waypoints = [{
        "latitude": coords[0][0],
        "longitude": coords[0][1],
        "description": None,
        "area_type": None
    }]
    accumulated_distance = 0.0

    for i in range(1, len(coords)):
        prev_lat, prev_lon = coords[i-1]
        curr_lat, curr_lon = coords[i]

        segment_distance = haversine_distance(prev_lat, prev_lon, curr_lat, curr_lon)
        accumulated_distance += segment_distance

        # Add point if we've traveled far enough
        if accumulated_distance >= interval_miles:
            waypoints.append({
                "latitude": curr_lat,
                "longitude": curr_lon,
                "description": None,
                "area_type": None
            })
            accumulated_distance = 0.0

    # Always include end point (if not already added)
    if len(coords) > 1:
        final_lat, final_lon = coords[-1]
        last_wp = waypoints[-1]

        # Check if end point is different from last waypoint
        distance_to_end = haversine_distance(
            last_wp["latitude"], last_wp["longitude"],
            final_lat, final_lon
        )

        # Add end point if it's more than 0.1 miles from last waypoint
        if distance_to_end > 0.1:
            waypoints.append({
                "latitude": final_lat,
                "longitude": final_lon,
                "description": None,
                "area_type": None
            })

    return waypoints


def classify_traffic(duration_normal: int, duration_traffic: int) -> Dict[str, Any]:
    """
    Classify traffic condition based on delay.

    Args:
        duration_normal: Normal duration in minutes (without traffic)
        duration_traffic: Duration with current traffic in minutes

    Returns:
        Dictionary with traffic information
    """
    delay = max(0, duration_traffic - duration_normal)

    # Calculate delay percentage
    if duration_normal > 0:
        delay_percent = (delay / duration_normal) * 100
    else:
        delay_percent = 0

    # Classify based on both absolute delay and percentage
    if delay < 5 and delay_percent < 10:
        condition = "light"
    elif delay < 15 and delay_percent < 30:
        condition = "moderate"
    else:
        condition = "heavy"

    return {
        "duration_in_traffic_minutes": duration_traffic,
        "traffic_delay_minutes": delay,
        "traffic_condition": condition
    }


# =============================================================================
# MAIN FUNCTION
# =============================================================================

def get_routes(
    start: str,
    destination: str,
    include_traffic: bool = True
) -> List[Dict[str, Any]]:
    """
    Get route alternatives between two addresses with adaptive waypoints.

    This function:
    1. Calls Google Directions API with alternatives=True
    2. Extracts route geometry from polylines
    3. Samples waypoints at adaptive intervals (denser in urban areas)
    4. Optionally fetches real-time traffic data
    5. Returns structured route data ready for crime analysis

    Args:
        start: Starting address (e.g., "Willis Tower, Chicago, IL")
        destination: Destination address (e.g., "Navy Pier, Chicago, IL")
        include_traffic: Whether to fetch real-time traffic data (default: True)

    Returns:
        List of route dictionaries, one per route alternative.
        Each route contains:
        - route_id: Unique identifier
        - summary: Route description (e.g., "I-90 W")
        - distance_miles: Total distance in miles
        - duration_minutes: Expected duration in minutes
        - start_address: Full starting address
        - end_address: Full ending address
        - waypoints: List of {latitude, longitude} points for crime analysis
        - polyline: Encoded polyline for visualization
        - traffic: Traffic information (if include_traffic=True)

    Raises:
        ValueError: If API key not set or invalid addresses

    Example:
        >>> routes = get_routes(
        ...     start="Willis Tower, Chicago, IL",
        ...     destination="Navy Pier, Chicago, IL"
        ... )
        >>> print(f"Found {len(routes)} routes")
        >>> print(f"Route 1: {routes[0]['distance_miles']} miles")
    """
    if not GOOGLE_API_KEY:
        raise ValueError(
            "GOOGLE_MAPS_API_KEY environment variable not set. "
            "Please add it to your .env file."
        )

    # Initialize Google Maps client
    gmaps = googlemaps.Client(key=GOOGLE_API_KEY)

    # Build directions request parameters
    directions_params = {
        "origin": start,
        "destination": destination,
        "mode": "driving",
        "alternatives": True,  # Request multiple routes
    }

    # Add traffic data request (requires departure_time)
    if include_traffic:
        directions_params["departure_time"] = "now"
        directions_params["traffic_model"] = "best_guess"

    # Call Google Directions API
    try:
        directions_result = gmaps.directions(**directions_params)
    except googlemaps.exceptions.ApiError as e:
        raise ValueError(f"Google Maps API error: {e}")
    except Exception as e:
        raise ValueError(f"Failed to get directions: {e}")

    if not directions_result:
        raise ValueError(
            f"No routes found between '{start}' and '{destination}'. "
            "Please check the addresses are valid."
        )

    routes = []

    for idx, route in enumerate(directions_result):
        # Extract the first leg (for direct A to B routes)
        leg = route["legs"][0]

        # Extract distance and duration
        distance_meters = leg["distance"]["value"]
        distance_miles = distance_meters / 1609.34

        duration_seconds = leg["duration"]["value"]
        duration_minutes = duration_seconds // 60

        # Get traffic info if available
        traffic_info = None
        if include_traffic and "duration_in_traffic" in leg:
            traffic_seconds = leg["duration_in_traffic"]["value"]
            traffic_minutes = traffic_seconds // 60
            traffic_info = classify_traffic(int(duration_minutes), int(traffic_minutes))

        # Get overview polyline (encoded path)
        overview_polyline = route["overview_polyline"]["points"]

        # Calculate adaptive sampling interval
        interval = get_adaptive_interval(distance_miles)

        # Sample waypoints from polyline
        waypoints = sample_points_from_polyline(
            encoded_polyline=overview_polyline,
            interval_miles=interval
        )

        # Create route dictionary
        route_data = {
            "route_id": idx + 1,
            "summary": route.get("summary", f"Route {idx + 1}"),
            "distance_miles": round(distance_miles, 2),
            "duration_minutes": int(duration_minutes),
            "start_address": leg["start_address"],
            "end_address": leg["end_address"],
            "waypoints": waypoints,
            "polyline": overview_polyline,
            "traffic": traffic_info
        }

        routes.append(route_data)

    return routes


# =============================================================================
# CLI TESTING
# =============================================================================

if __name__ == "__main__":
    """Quick test of the Google Maps helper."""
    import json

    print("=" * 60)
    print("Google Maps Final Helper - Test")
    print("=" * 60)

    try:
        routes = get_routes(
            start="Willis Tower, Chicago, IL",
            destination="Navy Pier, Chicago, IL",
            include_traffic=True
        )

        print(f"\nFound {len(routes)} route(s)\n")

        for route in routes:
            print(f"Route {route['route_id']}: {route['summary']}")
            print(f"  Distance: {route['distance_miles']} miles")
            print(f"  Duration: {route['duration_minutes']} minutes")
            print(f"  Waypoints: {len(route['waypoints'])}")

            if route['traffic']:
                print(f"  Traffic: {route['traffic']['traffic_condition']} "
                      f"(+{route['traffic']['traffic_delay_minutes']} min delay)")

            print()

        # Save to JSON for inspection
        output = {
            "test_metadata": {
                "start_address": "Willis Tower, Chicago, IL",
                "destination_address": "Navy Pier, Chicago, IL",
                "num_routes_found": len(routes)
            },
            "routes": routes
        }

        with open("test_output.json", "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print("Results saved to test_output.json")

    except Exception as e:
        print(f"Error: {e}")
