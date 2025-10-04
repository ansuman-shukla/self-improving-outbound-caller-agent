"""
API Test Script for Phase 2, Sub-phase 2.1
Tests the Scenarios endpoints
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def setup_test_personality():
    """Create a test personality to use for scenario generation"""
    print("\n" + "="*60)
    print("SETUP: Creating test personality")
    print("="*60)
    
    personality_data = {
        "name": "Struggling Parent",
        "description": "A single parent dealing with financial hardship",
        "core_traits": {
            "Attitude": "Anxious but cooperative",
            "Communication Style": "Honest and worried",
            "Financial Situation": "Limited income, trying their best"
        },
        "system_prompt": "You are a single parent who is genuinely struggling financially. You want to pay your debts but are finding it difficult. You are anxious about the situation but willing to cooperate and find a solution. You care about your credit score and your children's future."
    }
    
    response = requests.post(f"{BASE_URL}/personalities", json=personality_data)
    if response.status_code == 201:
        created = response.json()
        personality_id = created["_id"]
        print(f"✅ Created test personality: {created['name']} (ID: {personality_id})")
        return personality_id
    else:
        print(f"❌ Failed to create personality: {response.text}")
        return None


def test_scenarios(personality_id):
    """Test Scenario CRUD operations"""
    print("\n" + "="*60)
    print("TESTING SCENARIOS ENDPOINTS")
    print("="*60)
    
    # 1. Generate a scenario using AI
    print("\n1. Generating a scenario with AI...")
    scenario_data = {
        "personality_id": personality_id,
        "brief": "just lost their job due to company downsizing"
    }
    
    print(f"   Request: {json.dumps(scenario_data, indent=2)}")
    print("   ⏳ Calling Gemini API (this may take a few seconds)...")
    
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/scenarios/generate", json=scenario_data)
    elapsed = time.time() - start_time
    
    print(f"   Status: {response.status_code} (took {elapsed:.2f} seconds)")
    if response.status_code == 201:
        created = response.json()
        scenario_id = created["_id"]
        print(f"   ✅ Generated scenario:")
        print(f"      ID: {scenario_id}")
        print(f"      Title: {created['title']}")
        print(f"      Brief: {created['brief']}")
        print(f"      Backstory (excerpt): {created['backstory'][:150]}...")
        print(f"      Objective (excerpt): {created['objective'][:150]}...")
        print(f"      Weight: {created['weight']}")
    else:
        print(f"   ❌ Failed: {response.text}")
        return
    
    # 2. Get all scenarios
    print("\n2. Getting all scenarios...")
    response = requests.get(f"{BASE_URL}/scenarios")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        scenarios = response.json()
        print(f"   ✅ Found {len(scenarios)} scenarios")
        for idx, s in enumerate(scenarios, 1):
            print(f"      {idx}. {s['title']} (Weight: {s['weight']})")
    else:
        print(f"   ❌ Failed: {response.text}")
    
    # 3. Get single scenario
    print(f"\n3. Getting scenario by ID: {scenario_id}...")
    response = requests.get(f"{BASE_URL}/scenarios/{scenario_id}")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        scenario = response.json()
        print(f"   ✅ Retrieved: {scenario['title']}")
        print(f"      Full Backstory: {scenario['backstory']}")
        print(f"      Full Objective: {scenario['objective']}")
    else:
        print(f"   ❌ Failed: {response.text}")
    
    # 4. Update scenario (edit backstory and weight)
    print(f"\n4. Updating scenario (backstory and weight)...")
    update_data = {
        "backstory": "This debtor is a single parent who recently lost their job due to unexpected company downsizing. They have two young children and are now struggling to make ends meet. They have been actively job hunting but haven't found anything yet. They are worried about their mounting debts but are committed to finding a solution once they secure new employment.",
        "weight": 5
    }
    
    print(f"   Update data: {json.dumps(update_data, indent=2)}")
    response = requests.put(f"{BASE_URL}/scenarios/{scenario_id}", json=update_data)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        updated = response.json()
        print(f"   ✅ Updated scenario")
        print(f"      New weight: {updated['weight']}")
        print(f"      New backstory (excerpt): {updated['backstory'][:150]}...")
    else:
        print(f"   ❌ Failed: {response.text}")
    
    # 5. Update only weight
    print(f"\n5. Updating only weight...")
    update_data = {
        "weight": 4
    }
    
    response = requests.put(f"{BASE_URL}/scenarios/{scenario_id}", json=update_data)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        updated = response.json()
        print(f"   ✅ Updated weight to: {updated['weight']}")
    else:
        print(f"   ❌ Failed: {response.text}")
    
    # 6. Generate another scenario
    print("\n6. Generating a second scenario...")
    scenario_data_2 = {
        "personality_id": personality_id,
        "brief": "medical emergency drained their savings"
    }
    
    print("   ⏳ Calling Gemini API again...")
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/scenarios/generate", json=scenario_data_2)
    elapsed = time.time() - start_time
    
    print(f"   Status: {response.status_code} (took {elapsed:.2f} seconds)")
    if response.status_code == 201:
        created = response.json()
        scenario_id_2 = created["_id"]
        print(f"   ✅ Generated second scenario:")
        print(f"      ID: {scenario_id_2}")
        print(f"      Title: {created['title']}")
    else:
        print(f"   ❌ Failed: {response.text}")
        scenario_id_2 = None
    
    # 7. Get all scenarios again
    print("\n7. Getting all scenarios (should show 2 now)...")
    response = requests.get(f"{BASE_URL}/scenarios")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        scenarios = response.json()
        print(f"   ✅ Found {len(scenarios)} scenarios")
        for idx, s in enumerate(scenarios, 1):
            print(f"      {idx}. {s['title']} (Weight: {s['weight']})")
    else:
        print(f"   ❌ Failed: {response.text}")
    
    # 8. Delete first scenario
    print(f"\n8. Deleting first scenario...")
    response = requests.delete(f"{BASE_URL}/scenarios/{scenario_id}")
    print(f"   Status: {response.status_code}")
    if response.status_code == 204:
        print(f"   ✅ Deleted scenario")
    else:
        print(f"   ❌ Failed: {response.text}")
    
    # 9. Delete second scenario (if it exists)
    if scenario_id_2:
        print(f"\n9. Deleting second scenario...")
        response = requests.delete(f"{BASE_URL}/scenarios/{scenario_id_2}")
        print(f"   Status: {response.status_code}")
        if response.status_code == 204:
            print(f"   ✅ Deleted scenario")
        else:
            print(f"   ❌ Failed: {response.text}")
    
    # 10. Verify all scenarios are deleted
    print("\n10. Verifying scenarios are deleted...")
    response = requests.get(f"{BASE_URL}/scenarios")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        scenarios = response.json()
        print(f"   ✅ Found {len(scenarios)} scenarios (should be 0 or only have others)")
    else:
        print(f"   ❌ Failed: {response.text}")


def cleanup_test_personality(personality_id):
    """Clean up the test personality"""
    print("\n" + "="*60)
    print("CLEANUP: Deleting test personality")
    print("="*60)
    
    response = requests.delete(f"{BASE_URL}/personalities/{personality_id}")
    if response.status_code == 204:
        print(f"✅ Deleted test personality")
    else:
        print(f"❌ Failed to delete personality: {response.text}")


def main():
    """Run all scenario tests"""
    print("\n" + "="*60)
    print("PHASE 2 SUB-PHASE 2.1: SCENARIO API TESTS")
    print("="*60)
    print("\nThis will test:")
    print("  - POST /scenarios/generate (with AI)")
    print("  - GET /scenarios")
    print("  - GET /scenarios/{id}")
    print("  - PUT /scenarios/{id}")
    print("  - DELETE /scenarios/{id}")
    print("\nMake sure the backend is running on http://localhost:8000")
    
    input("\nPress ENTER to start tests...")
    
    # Setup
    personality_id = setup_test_personality()
    if not personality_id:
        print("\n❌ Setup failed, cannot continue")
        return
    
    try:
        # Run tests
        test_scenarios(personality_id)
    finally:
        # Cleanup
        cleanup_test_personality(personality_id)
    
    print("\n" + "="*60)
    print("✅ ALL TESTS COMPLETED")
    print("="*60)


if __name__ == "__main__":
    main()
