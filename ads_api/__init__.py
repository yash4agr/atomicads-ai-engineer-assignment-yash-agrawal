# Meta Ads API module

from .meta_ads import (
    check_api_access,
    get_ad_account_id,
    create_campaign,
    create_ad_set,
    create_ad,
    get_campaign_details
)

from .utils import (
    handle_api_error,
    format_targeting_spec,
    get_page_id
)

__all__ = [
    'check_api_access',
    'get_ad_account_id',
    'create_campaign',
    'create_ad_set',
    'create_ad',
    'get_campaign_details',
    'handle_api_error',
    'format_targeting_spec',
    'get_page_id'
]