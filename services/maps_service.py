"""
Google Maps Platform Service for VoteWise AI

Provides polling booth guidance and location services.
Features:
- Find nearest polling booth
- Geocoding/Reverse geocoding
- Maps embedding
- Route directions
- Location-based election help
"""

import requests
import json
from typing import Optional, Dict, Any, List
from config import Config


def get_nearby_polling_booths(lat, lng):
    """
    Backward-compatible function for finding polling booths.
    (Legacy API for routes/polling.py)
    """
    service = MapsService()
    return service.find_polling_booth(lat, lng)


class MapsService:
    """Google Maps Platform integration for polling guidance."""

    def __init__(self):
        self.api_key = Config.GOOGLE_MAPS_API_KEY
        self.base_url = "https://maps.googleapis.com/maps/api"

    def find_polling_booth(
        self, lat: float, lng: float, radius: int = 5000
    ) -> Optional[Dict[str, Any]]:
        """
        Find nearest polling booth location.

        Args:
            lat: User latitude
            lng: User longitude
            radius: Search radius in meters

        Returns:
            Polling booth data or None
        """
        if not self.api_key:
            return self._mock_polling_booth(lat, lng)

        url = f"{self.base_url}/place/nearbysearch/json"
        params = {
            "location": f"{lat},{lng}",
            "radius": radius,
            "type": "school|local_government_office|community_center",
            "key": self.api_key,
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if data.get("status") == "OK" and data.get("results"):
                place = data["results"][0]
                return self._format_booth_data(place, lat, lng)

            return self._mock_polling_booth(lat, lng)
        except requests.RequestException as e:
            print(f"Maps API Error: {e}")
            return self._mock_polling_booth(lat, lng)

    def find_multiple_booths(
        self, lat: float, lng: float, radius: int = 10000, max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find multiple polling booth options.

        Args:
            lat: User latitude
            lng: User longitude
            radius: Search radius in meters
            max_results: Maximum booths to return

        Returns:
            List of polling booth data
        """
        if not self.api_key:
            return [self._mock_polling_booth(lat, lng)]

        url = f"{self.base_url}/place/nearbysearch/json"
        params = {
            "location": f"{lat},{lng}",
            "radius": radius,
            "type": "school|local_government_office|community_center",
            "key": self.api_key,
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            booths = []
            if data.get("status") == "OK" and data.get("results"):
                for place in data["results"][:max_results]:
                    booths.append(self._format_booth_data(place, lat, lng))

            return booths if booths else [self._mock_polling_booth(lat, lng)]
        except requests.RequestException as e:
            print(f"Maps API Error: {e}")
            return [self._mock_polling_booth(lat, lng)]

    def geocode(self, address: str) -> Optional[Dict[str, Any]]:
        """
        Convert address to coordinates.

        Args:
            address: Street address

        Returns:
            Location data with lat/lng
        """
        if not self.api_key:
            return None

        url = f"{self.base_url}/geocode/json"
        params = {"address": address, "key": self.api_key}

        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if data.get("status") == "OK" and data.get("results"):
                result = data["results"][0]
                location = result["geometry"]["location"]
                return {
                    "lat": location["lat"],
                    "lng": location["lng"],
                    "formatted_address": result.get("formatted_address"),
                }
        except requests.RequestException:
            pass

        return None

    def reverse_geocode(self, lat: float, lng: float) -> Optional[str]:
        """
        Convert coordinates to readable address.

        Args:
            lat: Latitude
            lng: Longitude

        Returns:
            Formatted address string
        """
        if not self.api_key:
            return "Location coordinates provided"

        url = f"{self.base_url}/geocode/json"
        params = {"latlng": f"{lat},{lng}", "key": self.api_key}

        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if data.get("status") == "OK" and data.get("results"):
                return data["results"][0].get("formatted_address")
        except requests.RequestException:
            pass

        return f"Lat: {lat}, Lng: {lng}"

    def get_directions(
        self, origin_lat: float, origin_lng: float, dest_lat: float, dest_lng: float
    ) -> Optional[Dict[str, Any]]:
        """
        Get directions between two points.

        Args:
            origin_lat: Starting latitude
            origin_lng: Starting longitude
            dest_lat: Destination latitude
            dest_lng: Destination longitude

        Returns:
            Directions data with route info
        """
        if not self.api_key:
            return self._mock_directions(origin_lat, origin_lng, dest_lat, dest_lng)

        url = f"{self.base_url}/directions/json"
        params = {
            "origin": f"{origin_lat},{origin_lng}",
            "destination": f"{dest_lat},{dest_lng}",
            "mode": "walking",
            "key": self.api_key,
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if data.get("status") == "OK" and data.get("routes"):
                route = data["routes"][0]
                legs = route["legs"][0]
                return {
                    "distance": legs["distance"]["text"],
                    "duration": legs["duration"]["text"],
                    "start_address": legs["start_address"],
                    "end_address": legs["end_address"],
                    "steps": [
                        {
                            "distance": step["distance"]["text"],
                            "duration": step["duration"]["text"],
                            "instruction": step["html_instructions"],
                        }
                        for step in legs["steps"]
                    ],
                }
        except requests.RequestException:
            pass

        return self._mock_directions(origin_lat, origin_lng, dest_lat, dest_lng)

    def get_static_map_url(
        self, lat: float, lng: float, zoom: int = 15, size: str = "400x300"
    ) -> str:
        """
        Generate static map image URL.

        Args:
            lat: Center latitude
            lng: Center longitude
            zoom: Zoom level
            size: Image size

        Returns:
            Static map URL
        """
        if not self.api_key:
            return f"https://maps.google.com/?q={lat},{lng}"

        return (
            f"{self.base_url}/staticmap"
            f"?center={lat},{lng}"
            f"&zoom={zoom}"
            f"&size={size}"
            f"&markers=color:red|{lat},{lng}"
            f"&key={self.api_key}"
        )

    def get_embed_html(self, lat: float, lng: float, zoom: int = 15) -> str:
        """
        Generate embedded map iframe HTML.

        Args:
            lat: Center latitude
            lng: Center longitude
            zoom: Zoom level

        Returns:
            Iframe HTML string
        """
        if not self.api_key:
            return f'<iframe src="https://maps.google.com/?q={lat},{lng}&output=svembed" width="100%" height="400"></iframe>'

        return (
            f"<iframe "
            f'src="https://www.google.com/maps/embed/v1/place?key={self.api_key}'
            f"&q={lat},{lng}"
            f'&zoom={zoom}" '
            f'width="100%" height="400" style="border:0;" loading="lazy">'
            f"</iframe>"
        )

    def _format_booth_data(
        self, place: Dict, user_lat: float, user_lng: float
    ) -> Dict[str, Any]:
        """Format place data to booth format."""
        location = place.get("geometry", {}).get("location", {})
        place_lat = location.get("lat", 0)
        place_lng = location.get("lng", 0)

        return {
            "booth_name": place.get("name", "Local Polling Booth"),
            "address": place.get("vicinity", place.get("formatted_address", "")),
            "place_id": place.get("place_id"),
            "lat": place_lat,
            "lng": place_lng,
            "map_link": (
                f"https://www.google.com/maps/search/?api=1&query={place_lat},{place_lng}"
                f"&query_place_id={place.get('place_id')}"
            ),
            "directions_link": (
                f"https://www.google.com/maps/dir/?api=1"
                f"&destination={place_lat},{place_lng}"
            ),
            "rating": place.get("rating"),
            "user_ratings_total": place.get("user_ratings_total"),
            "opening_hours": place.get("opening_hours", {}).get("weekday_text", []),
            "types": place.get("types", []),
        }

    def _mock_polling_booth(self, lat: float, lng: float) -> Dict[str, Any]:
        """Mock polling booth when API unavailable."""
        return {
            "booth_name": "Community Center Polling Station",
            "address": "123 Election Road, Your Constituency",
            "place_id": "mock_place",
            "lat": lat + 0.01,
            "lng": lng + 0.01,
            "map_link": f"https://maps.google.com/?q={lat},{lng}",
            "directions_link": f"https://maps.google.com/dir/?api=1&destination={lat},{lng}",
            "rating": 4.2,
            "user_ratings_total": 50,
            "opening_hours": ["Monday: 9:00 AM - 5:00 PM"],
            "types": ["local_government_office"],
        }

    def _mock_directions(
        self, o_lat: float, o_lng: float, d_lat: float, d_lng: float
    ) -> Dict[str, Any]:
        """Mock directions when API unavailable."""
        return {
            "distance": "1.2 km",
            "duration": "15 mins",
            "start_address": f"Location ({o_lat}, {o_lng})",
            "end_address": f"Polling Station ({d_lat}, {d_lng})",
            "steps": [
                {
                    "distance": "500 m",
                    "duration": "6 mins",
                    "instruction": "Head north on Main Road",
                },
                {
                    "distance": "700 m",
                    "duration": "9 mins",
                    "instruction": "Turn right at the intersection",
                },
                {
                    "distance": "200 m",
                    "duration": "3 mins",
                    "instruction": "Destination will be on the right",
                },
            ],
        }


maps_service = MapsService()
