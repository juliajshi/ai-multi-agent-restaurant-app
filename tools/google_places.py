import os
import requests
from typing import List, Dict, Optional
from langchain_core.tools import tool
from typing import Annotated


@tool
def search_places_nearby(
    latitude: Annotated[float, "Latitude of the search center"],
    longitude: Annotated[float, "Longitude of the search center"],
    # included_types: Annotated[List[str], "List of place types to include (e.g., ['restaurant', 'cafe'])"] = ["restaurant"],
    preferences: Annotated[str, "describes the groups's preferences"],
    # max_result_count: Annotated[int, "Maximum number of results to return"] = 20,
    radius: Annotated[float, "Search radius in meters"] = 5000.0,
    field_mask: Annotated[
        str, "Fields to include in the response"
    ] = "places.displayName,places.rating,places.userRatingCount,places.formattedAddress,places.types,places.priceLevel",
) -> List[Dict]:
    """
    Search for places near a given location using Google Places (New) API.
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        return [{"error": "Google Maps API key not found"}]

    try:
        places_url = "https://places.googleapis.com/v1/places:searchText"

        # Build request body
        request_body = {
            "textQuery": preferences,
            "includedType": "restaurant",
            "maxResultCount": 20,
            "locationBias": {
                "circle": {
                    "center": {"latitude": latitude, "longitude": longitude},
                    "radius": radius,
                }
            },
        }

        # Set headers
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": field_mask,
        }

        # Make the API request
        response = requests.post(places_url, json=request_body, headers=headers)

        if response.status_code == 200:
            data = response.json()
            places_list = data.get("places", [])

            # Format the results
            formatted_places = []
            for place in places_list:
                formatted_place = {
                    "name": place.get("displayName", {}).get("text", "Unknown"),
                    "address": place.get("formattedAddress", "N/A"),
                    "rating": place.get("rating", "N/A"),
                    "user_ratings_total": place.get("userRatingCount", 0),
                    "types": place.get("types", []),
                    "price_level": place.get("priceLevel", "PRICE_LEVEL_MODERATE"),
                }
                formatted_places.append(formatted_place)

            return formatted_places
        else:
            return [
                {
                    "error": f"API request failed with status {response.status_code}: {response.text}"
                }
            ]

    except Exception as e:
        return [{"error": f"Error calling Google Places API: {str(e)}"}]
