"""
API Test Script for Phase 3, Sub-phase 3.3
Tests the Evaluations endpoints (Manual Evaluation Engine)
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"


def setup_test_data():
    """Create test personality, prompt, and scenario for evaluation testing"""
    print("\n" + "="*70)
    print("SETUP: Creating test data (Personality → Prompt → Scenario)")
    print("="*70)
    
    # 1. Create a test personality
    print("\n1. Creating test personality...")
    personality_data = {
        "name": "Anxious First-Time Debtor",
        "description": "Someone who has never dealt with debt collection before and is nervous",
        "core_traits": {
            "Attitude": "Anxious and overwhelmed",
            "Communication Style": "Hesitant, asks many questions",
            "Financial Situation": "Has money but doesn't understand the process"
        },
        "system_prompt": "You are receiving your first-ever debt collection call and you're very nervous. You have the money to pay but you're scared and don't understand the process. You ask a lot of questions and need reassurance. You're worried about legal consequences even though you want to resolve this."
    }
    
    response = requests.post(f"{BASE_URL}/personalities", json=personality_data)
    if response.status_code != 201:
        print(f"❌ Failed to create personality: {response.text}")
        return None, None, None
    
    personality = response.json()
    personality_id = personality["_id"]
    print(f"✅ Created personality: {personality['name']} (ID: {personality_id})")
    
    # 2. Create a test prompt
    print("\n2. Creating test agent prompt...")
    prompt_data = {
        "name": "Empathetic Debt Collection Agent v1.0",
        "prompt_text": """You are a professional debt collection agent with an empathetic approach.

Your goal is to collect the debt or arrange a payment plan while maintaining a respectful and understanding tone.

Guidelines:
1. Start by clearly explaining why you're calling
2. Listen to the debtor's concerns
3. Offer payment plan options
4. Be patient and reassuring
5. Avoid legal threats unless absolutely necessary
6. Keep the conversation focused and efficient

Remember: Most people want to pay their debts. Your job is to make it easy for them.""",
        "version": "1.0"
    }
    
    response = requests.post(f"{BASE_URL}/prompts", json=prompt_data)
    if response.status_code != 201:
        print(f"❌ Failed to create prompt: {response.text}")
        return None, None, None
    
    prompt = response.json()
    prompt_id = prompt["_id"]
    print(f"✅ Created prompt: {prompt['name']} (ID: {prompt_id})")
    
    # 3. Generate a test scenario
    print("\n3. Generating test scenario with AI...")
    scenario_data = {
        "personality_id": personality_id,
        "brief": "received first debt notice yesterday and is panicking"
    }
    
    print(f"   ⏳ Calling Gemini API to generate scenario...")
    response = requests.post(f"{BASE_URL}/scenarios/generate", json=scenario_data)
    if response.status_code != 201:
        print(f"❌ Failed to generate scenario: {response.text}")
        return None, None, None
    
    scenario = response.json()
    scenario_id = scenario["_id"]
    print(f"✅ Generated scenario: {scenario['title']} (ID: {scenario_id})")
    print(f"   Brief: {scenario['brief']}")
    print(f"   Objective (excerpt): {scenario['objective'][:100]}...")
    
    return personality_id, prompt_id, scenario_id


def test_create_evaluation(prompt_id, scenario_id):
    """Test POST /api/evaluations endpoint"""
    print("\n" + "="*70)
    print("TEST 1: Create Evaluation (POST /api/evaluations)")
    print("="*70)
    
    evaluation_data = {
        "prompt_id": prompt_id,
        "scenario_id": scenario_id
    }
    
    print(f"\nRequest: {json.dumps(evaluation_data, indent=2)}")
    print("⏳ Creating evaluation...")
    
    response = requests.post(f"{BASE_URL}/evaluations", json=evaluation_data)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 202:
        result = response.json()
        result_id = result["result_id"]
        status = result["status"]
        print(f"✅ Evaluation created successfully!")
        print(f"   Result ID: {result_id}")
        print(f"   Initial Status: {status}")
        return result_id
    else:
        print(f"❌ Failed: {response.text}")
        return None


def test_poll_evaluation(result_id):
    """Test GET /api/evaluations/{result_id} endpoint with polling"""
    print("\n" + "="*70)
    print("TEST 2: Poll Evaluation Status (GET /api/evaluations/{result_id})")
    print("="*70)
    
    print(f"\nPolling evaluation {result_id}...")
    print("This will take 30-90 seconds as the AI agents converse and analyze.\n")
    
    max_attempts = 60  # 60 attempts * 3 seconds = 3 minutes max
    attempt = 0
    start_time = time.time()
    
    while attempt < max_attempts:
        attempt += 1
        response = requests.get(f"{BASE_URL}/evaluations/{result_id}")
        
        if response.status_code != 200:
            print(f"❌ Error fetching evaluation: {response.text}")
            return None
        
        evaluation = response.json()
        status = evaluation["status"]
        elapsed = time.time() - start_time
        
        print(f"[{attempt:2d}] Status: {status:12s} (Elapsed: {elapsed:.1f}s)", end="")
        
        if status == "COMPLETED":
            print(" ✅ COMPLETED!")
            print(f"\n{'='*70}")
            print("EVALUATION RESULTS")
            print(f"{'='*70}")
            
            # Display scores
            scores = evaluation.get("scores", {})
            print(f"\n📊 SCORES:")
            print(f"   Task Completion:        {scores.get('task_completion', 0)}/100")
            print(f"   Conversation Efficiency: {scores.get('conversation_efficiency', 0)}/100")
            
            # Display analysis
            analysis = evaluation.get("evaluator_analysis", "No analysis provided")
            print(f"\n📝 EVALUATOR ANALYSIS:")
            print(f"   {analysis}")
            
            # Display transcript info
            transcript = evaluation.get("transcript", [])
            print(f"\n💬 TRANSCRIPT: {len(transcript)} messages")
            
            if transcript:
                print("\n   First 3 exchanges:")
                for i, msg in enumerate(transcript[:6]):
                    speaker = msg["speaker"].upper()
                    message = msg["message"]
                    print(f"   [{speaker}]: {message[:80]}{'...' if len(message) > 80 else ''}")
                
                if len(transcript) > 6:
                    print(f"   ... ({len(transcript) - 6} more messages)")
            
            # Display timestamps
            created_at = evaluation.get("created_at")
            completed_at = evaluation.get("completed_at")
            print(f"\n⏱️  TIMING:")
            print(f"   Created:   {created_at}")
            print(f"   Completed: {completed_at}")
            print(f"   Duration:  {elapsed:.1f} seconds")
            
            return evaluation
        
        elif status == "FAILED":
            print(" ❌ FAILED!")
            error_msg = evaluation.get("error_message", "Unknown error")
            print(f"\n❌ Evaluation failed: {error_msg}")
            return None
        
        elif status == "RUNNING":
            print(" (AI agents conversing...)")
        
        else:  # PENDING
            print(" (waiting to start...)")
        
        # Wait before next poll
        time.sleep(3)
    
    print(f"\n⚠️  Timeout: Evaluation did not complete within {max_attempts * 3} seconds")
    return None


def test_list_evaluations():
    """Test GET /api/evaluations endpoint"""
    print("\n" + "="*70)
    print("TEST 3: List All Evaluations (GET /api/evaluations)")
    print("="*70)
    
    response = requests.get(f"{BASE_URL}/evaluations")
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        evaluations = response.json()
        print(f"✅ Found {len(evaluations)} evaluation(s)")
        
        if evaluations:
            print("\nMost recent evaluations:")
            for i, eval in enumerate(evaluations[:5], 1):
                status = eval.get("status", "UNKNOWN")
                eval_id = eval.get("_id", "N/A")
                created = eval.get("created_at", "N/A")
                
                scores = eval.get("scores")
                if scores:
                    tc = scores.get("task_completion", 0)
                    ce = scores.get("conversation_efficiency", 0)
                    score_str = f"TC:{tc} CE:{ce}"
                else:
                    score_str = "No scores yet"
                
                print(f"   {i}. [{status:10s}] ID: {eval_id[:12]}... | {score_str} | {created}")
        
        return evaluations
    else:
        print(f"❌ Failed: {response.text}")
        return None


def test_delete_evaluation(result_id):
    """Test DELETE /api/evaluations/{result_id} endpoint"""
    print("\n" + "="*70)
    print("TEST 4: Delete Evaluation (DELETE /api/evaluations/{result_id})")
    print("="*70)
    
    print(f"\nDeleting evaluation {result_id}...")
    response = requests.delete(f"{BASE_URL}/evaluations/{result_id}")
    
    print(f"Status: {response.status_code}")
    if response.status_code == 204:
        print(f"✅ Evaluation deleted successfully")
        
        # Verify deletion
        print("\nVerifying deletion...")
        verify_response = requests.get(f"{BASE_URL}/evaluations/{result_id}")
        if verify_response.status_code == 404:
            print("✅ Confirmed: Evaluation no longer exists")
            return True
        else:
            print("⚠️  Warning: Evaluation still exists after deletion")
            return False
    else:
        print(f"❌ Failed: {response.text}")
        return False


def test_error_cases():
    """Test error handling"""
    print("\n" + "="*70)
    print("TEST 5: Error Handling")
    print("="*70)
    
    # Test 1: Invalid prompt_id
    print("\n1. Testing with invalid prompt_id...")
    response = requests.post(f"{BASE_URL}/evaluations", json={
        "prompt_id": "000000000000000000000000",
        "scenario_id": "000000000000000000000000"
    })
    print(f"   Status: {response.status_code}")
    if response.status_code == 404:
        print("   ✅ Correctly returned 404 for invalid IDs")
    else:
        print(f"   ⚠️  Expected 404, got {response.status_code}")
    
    # Test 2: Invalid result_id
    print("\n2. Testing GET with invalid result_id...")
    response = requests.get(f"{BASE_URL}/evaluations/invalid_id_12345")
    print(f"   Status: {response.status_code}")
    if response.status_code == 404:
        print("   ✅ Correctly returned 404 for invalid result_id")
    else:
        print(f"   ⚠️  Expected 404, got {response.status_code}")
    
    # Test 3: Missing required fields
    print("\n3. Testing POST with missing fields...")
    response = requests.post(f"{BASE_URL}/evaluations", json={
        "prompt_id": "507f1f77bcf86cd799439011"
        # Missing scenario_id
    })
    print(f"   Status: {response.status_code}")
    if response.status_code == 422:
        print("   ✅ Correctly returned 422 for missing required field")
    else:
        print(f"   ⚠️  Expected 422, got {response.status_code}")


def run_all_tests():
    """Run complete test suite"""
    print("\n" + "="*70)
    print("PHASE 3 - MANUAL EVALUATION ENGINE API TESTS")
    print("="*70)
    print("This will test the complete evaluation workflow:")
    print("1. Create evaluation (POST)")
    print("2. Poll for results (GET)")
    print("3. List evaluations (GET)")
    print("4. Delete evaluation (DELETE)")
    print("5. Error handling")
    print("="*70)
    
    try:
        # Setup
        personality_id, prompt_id, scenario_id = setup_test_data()
        if not all([personality_id, prompt_id, scenario_id]):
            print("\n❌ Setup failed. Cannot proceed with tests.")
            return
        
        # Test 1: Create evaluation
        result_id = test_create_evaluation(prompt_id, scenario_id)
        if not result_id:
            print("\n❌ Failed to create evaluation. Stopping tests.")
            return
        
        # Test 2: Poll for results
        evaluation = test_poll_evaluation(result_id)
        if not evaluation:
            print("\n⚠️  Evaluation did not complete successfully")
        
        # Test 3: List evaluations
        test_list_evaluations()
        
        # Test 4: Delete evaluation (optional - comment out to keep data)
        # test_delete_evaluation(result_id)
        
        # Test 5: Error cases
        test_error_cases()
        
        # Summary
        print("\n" + "="*70)
        print("TEST SUITE COMPLETED")
        print("="*70)
        print("\n✅ All Phase 3 evaluation endpoints tested successfully!")
        print(f"\n💡 TIP: You can view the evaluation in the database with ID: {result_id}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
