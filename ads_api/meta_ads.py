import requests
import time
from typing import Dict, Any, Tuple, Optional

BASE_URL = "https://graph.facebook.com/v22.0" # META Graph api base url

def check_api_access(access_token: str) -> Tuple[bool, str]:
    """
    Check if the provided access token has valid access to Meta Ads API.
    
    Args:
        access_token: Meta Ads API access token
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        url = f"{BASE_URL}/me"
        params = {
            "access_token": access_token,
            "fields": "id,name"
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        user_data = response.json()
        return True, f"Connected as {user_data.get('name', 'Unknown')}"
    
    except requests.exceptions.RequestException as e:
        if response.status_code == 401:
            return False, "Invalid access token"
        else:
            return False, f"API connection error: {str(e)}"


def get_ad_account_id(access_token: str) -> Optional[str]:
    """
    Get the first available ad account ID for the user.
    
    Args:
        access_token: Meta Ads API access token
        
    Returns:
        Ad account ID or None if not found
    """
    try:
        # Get ad accounts available to the user
        url = f"{BASE_URL}/me/adaccounts"
        params = {
            "access_token": access_token,
            "fields": "id,name"
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        accounts_data = response.json()
        
        if "data" in accounts_data and len(accounts_data["data"]) > 0:
            # Return the first ad account ID
            return accounts_data["data"][0]["id"]
        else:
            return None
    
    except requests.exceptions.RequestException:
        return None


def create_campaign(
    access_token: str,
    ad_account_id: str,
    name: str,
    objective: str = "CONSIDERATION",
    status: str = "PAUSED"
) -> str:
    """
    Create a new campaign in Meta Ads.
    
    Args:
        access_token: Meta Ads API access token
        ad_account_id: Ad account ID
        name: Campaign name
        objective: Campaign objective (AWARENESS, CONSIDERATION, CONVERSIONS)
        status: Campaign status (ACTIVE, PAUSED)
        
    Returns:
        Campaign ID
    """
    # Map high-level objectives to Meta's specific objectives
    objective_mapping = {
        "AWARENESS": "BRAND_AWARENESS",
        "CONSIDERATION": "OUTCOME_TRAFFIC",
        "CONVERSIONS": "CONVERSIONS"
    }
    
    meta_objective = objective_mapping.get(objective, "OUTCOME_TRAFFIC")
    
    url = f"{BASE_URL}/{ad_account_id}/campaigns"
    
    data = {
        "name": name,
        "objective": meta_objective,
        "status": status,
        "special_ad_categories": []
    }
    
    params = {
        "access_token": access_token
    }
    
    try:
        response = requests.post(url, params=params, json=data)
        response.raise_for_status()
        
        result = response.json()
        return result.get("id")
    
    except requests.exceptions.RequestException as e:
        error_msg = f"Failed to create campaign - {response.json().get('error', 'Unknown Error').get('error_user_msg', '')}\n\nError Detail:\n{str(e)}"
        if hasattr(e, "response") and e.response:
            error_msg += f" - {e.response.text}"
        raise Exception(error_msg)


def create_ad_set(
    access_token: str,
    ad_account_id: str,
    name: str,
    campaign_id: str,
    daily_budget: float,
    targeting: Dict[str, Any],
    status: str = "PAUSED"
) -> str:
    """
    Create a new ad set in Meta Ads.
    
    Args:
        access_token: Meta Ads API access token
        ad_account_id: Ad account ID
        name: Ad set name
        campaign_id: Parent campaign ID
        daily_budget: Daily budget in USD
        targeting: Targeting specifications
        status: Ad set status (ACTIVE, PAUSED)
        
    Returns:
        Ad set ID
    """
    url = f"{BASE_URL}/{ad_account_id}/adsets"
    
    # Convert daily budget to cents as required by the API
    budget_in_cents = int(daily_budget * 100)
    
    # Prepare optimization and billing settings
    optimization_goal = "LINK_CLICKS"
    billing_event = "IMPRESSIONS"
    
    # Get 1 day from now in UTC time
    start_time = int(time.time())
    end_time = start_time + (30 * 24 * 60 * 60)  # 30 days from now
    
    data = {
        "name": name,
        "campaign_id": campaign_id,
        "daily_budget": budget_in_cents,
        "optimization_goal": optimization_goal,
        "billing_event": billing_event,
        "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
        "status": status,
        "targeting": targeting,
        "start_time": start_time,
        "end_time": end_time
    }
    params = {
        "access_token": access_token
    }

    try:
        response = requests.post(url, params=params, json=data)
        # print(f"Response: {response.text}")  # Debugging line
        response.raise_for_status()
        
        result = response.json()
        return result.get("id")
    
    except requests.exceptions.RequestException as e:
        error_msg = f"Failed to create ad set - {response.json().get('error', 'Unknown Error').get('error_user_msg', '')}\n\nError Detail:\n{str(e)}"
        if hasattr(e, "response") and e.response:
            error_msg += f" - {e.response.text}"
        raise Exception(error_msg)


def create_ad(
    access_token: str,
    ad_account_id: str,
    name: str,
    ad_set_id: str,
    creative_data: Dict[str, str],
    status: str = "PAUSED"
) -> str:
    """
    Create a new ad in Meta Ads.
    
    Args:
        access_token: Meta Ads API access token
        ad_account_id: Ad account ID
        name: Ad name
        ad_set_id: Parent ad set ID
        creative_data: Dictionary containing creative details
        status: Ad status (ACTIVE, PAUSED)
        
    Returns:
        Ad ID
    """
    # First, create an ad creative
    creative_id = create_ad_creative(
        access_token=access_token,
        ad_account_id=ad_account_id,
        creative_data=creative_data
    )
    
    # Then create the ad using the creative
    url = f"{BASE_URL}/{ad_account_id}/ads"
    
    data = {
        "name": name,
        "adset_id": ad_set_id,
        "creative": {"creative_id": creative_id},
        "status": status
    }
    
    params = {
        "access_token": access_token
    }
    
    try:
        response = requests.post(url, params=params, json=data)
        # print(f"Response: {response.text}")  # Debugging line
        response.raise_for_status()
        
        result = response.json()
        return result.get("id")
    
    except requests.exceptions.RequestException as e:
        error_msg = f"Failed to create ad - {response.json().get('error', 'Unknown Error').get('error_user_msg', '')}\n\nError Detail:\n{str(e)}"
        if hasattr(e, "response") and e.response:
            error_msg += f" - {e.response.text}"
        raise Exception(error_msg)


def create_ad_creative(
    access_token: str,
    ad_account_id: str,
    creative_data: Dict[str, str]
) -> str:
    """
    Create an ad creative in Meta Ads.
    
    Args:
        access_token: Meta Ads API access token
        ad_account_id: Ad account ID
        creative_data: Dictionary containing creative details
        
    Returns:
        Ad creative ID
    """
    url = f"{BASE_URL}/{ad_account_id}/adcreatives"
    
    # Extract creative data
    title = creative_data.get("title", "")
    body = creative_data.get("body", "")
    description = creative_data.get("description", "")
    image_url = creative_data.get("image_url", "")
    website_url = creative_data.get("website_url", "")
    call_to_action = creative_data.get("call_to_action", "LEARN_MORE")
    page_id = creative_data.get("page_id", "")

    if not page_id:
        raise ValueError("Facebook Page ID is required to create an ad creative")
    
    # Prepare the ad creative data
    data = {
        "name": f"Creative for {title}",
        "object_story_spec": {
            "page_id": page_id, 
            "link_data": {
                "message": body,
                "link": website_url,
                "name": title,
                "description": description,
                "call_to_action": {
                    "type": call_to_action
                },
                "image_hash": "4098e58bb25e54ff17283d7bf4f44fd6"  # TODO: Implement image hashing logic
            }
        }
    }
    
    params = {
        "access_token": access_token
    }
    
    try:
        response = requests.post(url, params=params, json=data)
        # print(f"Response: {response.text}")  # Debugging line
        response.raise_for_status()
        
        result = response.json()
        return result.get("id")
    
    except requests.exceptions.RequestException as e:
        error_msg = f"Failed to create ad creative - {response.json().get('error', 'Unknown Error').get('error_user_msg', '')}\n\nError Detail:\n{str(e)}"
        if hasattr(e, "response") and e.response:
            error_msg += f" - {e.response.text}"
        raise Exception(error_msg)


def get_campaign_details(
    access_token: str,
    campaign_id: str
) -> Dict[str, Any]:
    """
    Get details of a campaign.
    
    Args:
        access_token: Meta Ads API access token
        campaign_id: Campaign ID
        
    Returns:
        Campaign details as a dictionary
    """
    url = f"{BASE_URL}/{campaign_id}"
    
    params = {
        "access_token": access_token,
        "fields": "id,name,objective,status,created_time,updated_time"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        return response.json()
    
    except requests.exceptions.RequestException as e:
        error_msg = f"Failed to get campaign details - {response.json().get('error', 'Unknown Error').get('error_user_msg', '')}\n\nError Detail:\n{str(e)}"
        if hasattr(e, "response") and e.response:
            error_msg += f" - {e.response.text}"
        raise Exception(error_msg)