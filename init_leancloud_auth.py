import requests
import json

# Configuration
LC_APP_ID = "nFidWX8hhSHJOh7KRWO2a2Yg-gzGzoHsz"
LC_APP_KEY = "eDvvAo2y5GPJkorc0dWkXA7y"
LC_SERVER_URL = "https://nfidwx8h.lc-cn-n1-shared.com"

# Class for storing app configuration
CLASS_NAME = "AppConfig"

def init_password():
    base_url = f"{LC_SERVER_URL}/1.1/classes/{CLASS_NAME}"
    headers = {
        "X-LC-Id": LC_APP_ID,
        "X-LC-Key": LC_APP_KEY,
        "Content-Type": "application/json"
    }

    # 1. Check if config exists
    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()
        results = response.json().get("results", [])
        
        # Look for "admin_password" key
        config_item = None
        for item in results:
            if item.get("key") == "admin_password":
                config_item = item
                break
        
        if config_item:
            print(f"Password config already exists (ObjectId: {config_item['objectId']}). Updating...")
            # Update
            update_url = f"{base_url}/{config_item['objectId']}"
            data = {"value": "Key123456"} # Default password
            requests.put(update_url, headers=headers, json=data)
            print("Password updated to 'Key123456'")
        else:
            print("Creating new password config...")
            # Create
            data = {
                "key": "admin_password",
                "value": "Key123456"
            }
            requests.post(base_url, headers=headers, json=data)
            print("Password initialized to 'Key123456'")
            
    except Exception as e:
        print(f"Error initializing password: {e}")

if __name__ == "__main__":
    init_password()
