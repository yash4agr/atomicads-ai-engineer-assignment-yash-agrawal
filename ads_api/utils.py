import requests
import json
from typing import Dict, Any, Optional

def handle_api_error(response: requests.Response) -> Dict[str, Any]:
    """
    Handle API error responses by extracting error information.
    
    Args:
        response: Response object from requests
        
    Returns:
        Dictionary with error details
    """
    try:
        error_data = response.json()
        
        if "error" in error_data:
            error_info = error_data["error"]
            return {
                "error_code": error_info.get("code", "unknown"),
                "error_message": error_info.get("message", "Unknown error"),
                "error_type": error_info.get("type", "unknown"),
                "error_subcode": error_info.get("error_subcode", "unknown")
            }
        
        return {
            "error_code": response.status_code,
            "error_message": "Unknown API error",
            "error_type": "api_error",
            "error_subcode": "unknown"
        }
    
    except json.JSONDecodeError:
        return {
            "error_code": response.status_code,
            "error_message": response.text or "Unknown API error",
            "error_type": "api_error",
            "error_subcode": "invalid_json"
        }


def format_targeting_spec(targeting_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format targeting specification for Meta Ads API.
    
    Args:
        targeting_data: Raw targeting data from user input
        
    Returns:
        Formatted targeting specification for API
    """
    targeting_spec = {}
    
    # Age targeting
    if "age_min" in targeting_data:
        targeting_spec["age_min"] = targeting_data["age_min"]
    if "age_max" in targeting_data:
        targeting_spec["age_max"] = targeting_data["age_max"]
    
    # Gender targeting
    if "genders" in targeting_data:
        # Convert string gender to list of integers
        # 1 = male, 2 = female
        genders = targeting_data["genders"]
        if isinstance(genders, list) and len(genders) > 0:
            targeting_spec["genders"] = genders
    
    # Location targeting
    if "geo_locations" in targeting_data:
        targeting_spec["geo_locations"] = targeting_data["geo_locations"]
    elif "locations" in targeting_data:
        # Format locations as expected by the API
        locations = targeting_data["locations"]
        if isinstance(locations, list) and len(locations) > 0:
            targeting_spec["geo_locations"] = {
                "countries": locations if all(len(loc) == 2 for loc in locations) else [],
                "cities": [],
                "regions": []
            }
    
    # Interests targeting
    if "interests" in targeting_data and isinstance(targeting_data["interests"], list):
        targeting_spec["interests"] = [
            {"id": interest_id, "name": interest_name}
            for interest_id, interest_name in targeting_data["interests"]
        ]
    
    return targeting_spec


def get_page_id(access_token: str) -> Optional[str]:
    """
    Get the first available Facebook Page ID for the user.
    
    Args:
        access_token: Meta Ads API access token
        
    Returns:
        Page ID or None if not found
    """
    try:
        # Get pages available to the user
        url = "https://graph.facebook.com/v18.0/me/accounts"
        params = {
            "access_token": access_token,
            "fields": "id,name"
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        pages_data = response.json()
        
        if "data" in pages_data and len(pages_data["data"]) > 0:
            # Return the first page ID
            return pages_data["data"][0]["id"]
        else:
            return None
    
    except requests.exceptions.RequestException:
        return None