import os
import json
from typing import Dict, Any
from pathlib import Path
from dotenv import load_dotenv

def load_config() -> Dict[str, Any]:
    """
    Load configuration from .env file and config.json
    
    Returns:
        Dictionary containing config settings
    """
    # Load environment variables from .env file
    env_path = Path('.') / '.env'
    load_dotenv(dotenv_path=env_path, override=True)
    
    config = {
        "together_api_key": os.environ.get("TOGETHER_API_KEY", ""),
        "meta_access_token": os.environ.get("META_ACCESS_TOKEN", ""),
        "default_model": os.environ.get("DEFAULT_MODEL", "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"),
        "default_temp": float(os.environ.get("DEFAULT_TEMP", "0.7")),
        "log_level": os.environ.get("LOG_LEVEL", "INFO"),
        "use_test_mode": os.environ.get("USE_TEST_MODE", "false").lower() == "true"
    }
    
    # Try to load config from config.json if it exists
    config_path = Path('.') / 'config.json'
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                file_config = json.load(f)
                config.update(file_config)
        except (json.JSONDecodeError, IOError):
            #Just use the default values
            pass
    
    return config


def save_config(config: Dict[str, Any]) -> bool:
    """
    Save configuration to config.json
    
    Args:
        config: Dictionary containing config settings
        
    Returns:
        True if successful, False otherwise
    """
    config_path = Path('.') / 'config.json'
    
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except IOError:
        return False