"""
Quick API Test Script for Phase 1, Sub-phase 1.1
Tests the Personalities and Prompts endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_personalities():
    """Test Personality CRUD operations"""
    print("\n" + "="*60)
    print("TESTING PERSONALITIES ENDPOINTS")
    print("="*60)
    
    # 1. Create a personality
    print("\n1. Creating a personality...")
    personality_data = {
        "name": "Willful Defaulter",
        "description": "A person who has the means to pay but is avoiding payment",
        "core_traits": {
            "Attitude": "Cynical",
            "Communication Style": "Evasive",
            "Financial Situation": "Stable but uncooperative"
        },
        "system_prompt": "You are a debtor who has the financial means to pay but is choosing not to. You make excuses and try to avoid commitment. You are cynical about the process and evasive in your communication."
    }
    
    response = requests.post(f"{BASE_URL}/personalities", json=personality_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        created = response.json()
        personality_id = created["_id"]
        print(f"✅ Created personality: {created['name']} (ID: {personality_id})")
    else:
        print(f"❌ Failed: {response.text}")
        return
    
    # 2. Get all personalities
    print("\n2. Getting all personalities...")
    response = requests.get(f"{BASE_URL}/personalities")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Found {result['total']} personalities")
    else:
        print(f"❌ Failed: {response.text}")
    
    # 3. Get single personality
    print(f"\n3. Getting personality by ID: {personality_id}...")
    response = requests.get(f"{BASE_URL}/personalities/{personality_id}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        personality = response.json()
        print(f"✅ Retrieved: {personality['name']}")
    else:
        print(f"❌ Failed: {response.text}")
    
    # 4. Update personality
    print(f"\n4. Updating personality...")
    update_data = {
        "description": "Updated: A person who has means but refuses to pay"
    }
    response = requests.put(f"{BASE_URL}/personalities/{personality_id}", json=update_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        updated = response.json()
        print(f"✅ Updated description: {updated['description']}")
    else:
        print(f"❌ Failed: {response.text}")
    
    # 5. Delete personality
    print(f"\n5. Deleting personality...")
    response = requests.delete(f"{BASE_URL}/personalities/{personality_id}")
    print(f"Status: {response.status_code}")
    if response.status_code == 204:
        print(f"✅ Deleted personality")
    else:
        print(f"❌ Failed: {response.text}")


def test_prompts():
    """Test Prompt CRUD operations"""
    print("\n" + "="*60)
    print("TESTING PROMPTS ENDPOINTS")
    print("="*60)
    
    # 1. Create a prompt
    print("\n1. Creating a prompt...")
    prompt_data = {
        "name": "v1.1-empathetic",
        "prompt_text": "You are an empathetic debt collection agent. Your goal is to help customers find a payment solution that works for them while maintaining professionalism and compassion.",
        "version": "1.1"
    }
    
    response = requests.post(f"{BASE_URL}/prompts", json=prompt_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        created = response.json()
        prompt_id = created["_id"]
        print(f"✅ Created prompt: {created['name']} v{created['version']} (ID: {prompt_id})")
    else:
        print(f"❌ Failed: {response.text}")
        return
    
    # 2. Get all prompts
    print("\n2. Getting all prompts...")
    response = requests.get(f"{BASE_URL}/prompts")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Found {result['total']} prompts")
    else:
        print(f"❌ Failed: {response.text}")
    
    # 3. Get single prompt
    print(f"\n3. Getting prompt by ID: {prompt_id}...")
    response = requests.get(f"{BASE_URL}/prompts/{prompt_id}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        prompt = response.json()
        print(f"✅ Retrieved: {prompt['name']} v{prompt['version']}")
    else:
        print(f"❌ Failed: {response.text}")
    
    # 4. Update prompt
    print(f"\n4. Updating prompt...")
    update_data = {
        "version": "1.2"
    }
    response = requests.put(f"{BASE_URL}/prompts/{prompt_id}", json=update_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        updated = response.json()
        print(f"✅ Updated version to: {updated['version']}")
    else:
        print(f"❌ Failed: {response.text}")
    
    # 5. Delete prompt
    print(f"\n5. Deleting prompt...")
    response = requests.delete(f"{BASE_URL}/prompts/{prompt_id}")
    print(f"Status: {response.status_code}")
    if response.status_code == 204:
        print(f"✅ Deleted prompt")
    else:
        print(f"❌ Failed: {response.text}")


if __name__ == "__main__":
    print("\n🚀 Starting API Tests for Phase 1, Sub-phase 1.1")
    print(f"Base URL: {BASE_URL}")
    
    try:
        # Test health endpoint
        print("\n📍 Testing server health...")
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server is not responding properly")
            exit(1)
        
        # Run tests
        test_personalities()
        test_prompts()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
        print("="*60 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to the API server")
        print("Make sure the server is running: uvicorn main:app --reload")
        print("(from the backend directory)\n")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}\n")
