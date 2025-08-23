import os
import requests
from typing import List, Dict, Optional, TypedDict
from langchain_core.tools import tool
from typing import Annotated


@tool
def get_distance_matrix(
    origins: Annotated[
        List[List[float]],
        "contains member origin locations with latitude and longitude",
    ],
    destinations: Annotated[
        List[List[float]],
        "list of restaurant destination locations with latitude and longitude",
    ],
    mode: Annotated[
        str,
        "The mode of transportation. Can be DRIVE, TRANSIT, WALK, or BICYCLE.",
    ] = "DRIVE",
) -> List[Dict]:
    """
    Get the distance matrix between two locations.
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        return {"error": "Google Maps API key not found"}

    try:
        # Google Routes API endpoint
        url = "https://routes.googleapis.com/distanceMatrix/v2:computeRouteMatrix"

        # Build request body according to API documentation
        request_body = {
            "origins": [
                {
                    "waypoint": {
                        "location": {
                            "latLng": {
                                "latitude": origin[0],
                                "longitude": origin[1],
                            }
                        }
                    },
                    "routeModifiers": {"avoid_ferries": True},
                }
                for origin in origins
            ],
            "destinations": [
                {
                    "waypoint": {
                        "location": {
                            "latLng": {
                                "latitude": destination[0],
                                "longitude": destination[1],
                            }
                        }
                    }
                }
                for destination in destinations
            ],
            "travelMode": mode,
            "routingPreference": "TRAFFIC_AWARE",
        }

        # Set headers
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": "originIndex,destinationIndex,duration,distanceMeters,status,condition",
        }

        # Make the API request
        response = requests.post(url, json=request_body, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            return [
                {
                    "error": f"Routes API request failed with status {response.status_code}: {response.text}"
                }
            ]

    except Exception as e:
        return [{"error": f"Error calling Google Routes API: {str(e)}"}]
