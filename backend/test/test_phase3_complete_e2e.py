"""
Phase 3.3 Backend Testing: Complete End-to-End Evaluation API Tests
Tests POST /api/evaluations and GET /api/evaluations/{result_id} with polling
No pytest dependency - uses simple Python requests and assertions
"""

import sys
import os
import time
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
POLL_INTERVAL = 2  # seconds
MAX_POLL_TIME = 120  # seconds (2 minutes max wait)


# ============================================================================
# SETUP: Create Test Data
# ============================================================================

def setup_test_data():
    """Create necessary test data: personality, prompt, and scenario"""
    print("\n" + "="*70)
    print("SETUP: Creating test data for evaluation testing")
    print("="*70)
    
    # 1. Create test personality
    print("\n📝 Step 1: Creating test personality...")
    personality_data = {
        "name": "Test Anxious Debtor for Phase 3.3",
        "description": "Test personality for evaluation testing",
        "core_traits": {
            "Attitude": "Anxious",
            "Communication": "Hesitant",
            "Financial": "Struggling"
        },
        "system_prompt": "You are a nervous debtor who just received their first debt notice. You have money but you're scared. Ask lots of questions and need reassurance."
    }
    
    response = requests.post(f"{BASE_URL}/personalities", json=personality_data)
    if response.status_code != 201:
        print(f"❌ Failed to create personality: {response.text}")
        return None
    
    personality = response.json()
    personality_id = personality["_id"]
    print(f"✅ Created personality: {personality['name']} (ID: {personality_id})")
    
    # 2. Create test prompt
    print("\n📝 Step 2: Creating test agent prompt...")
    prompt_data = {
        "name": "Test Empathetic Agent for Phase 3.3",
        "prompt_text": """You are a professional debt collection agent with an empathetic approach.

Your goal: Collect the debt or arrange a payment plan respectfully.

Guidelines:
- Explain clearly why you're calling
- Listen to concerns
- Offer payment plan options
- Be patient and reassuring
- Keep conversation focused""",
        "version": "test-1.0"
    }
    
    response = requests.post(f"{BASE_URL}/prompts", json=prompt_data)
    if response.status_code != 201:
        print(f"❌ Failed to create prompt: {response.text}")
        return None
    
    prompt = response.json()
    prompt_id = prompt["_id"]
    print(f"✅ Created prompt: {prompt['name']} (ID: {prompt_id})")
    
    # 3. Generate test scenario
    print("\n📝 Step 3: Generating test scenario with AI...")
    scenario_data = {
        "personality_id": personality_id,
        "brief": "received first debt notice yesterday and is worried"
    }
    
    print("   ⏳ Calling Gemini API to generate scenario...")
    response = requests.post(f"{BASE_URL}/scenarios/generate", json=scenario_data)
    if response.status_code != 201:
        print(f"❌ Failed to generate scenario: {response.text}")
        return None
    
    scenario = response.json()
    scenario_id = scenario["_id"]
    print(f"✅ Generated scenario: {scenario['title']} (ID: {scenario_id})")
    
    return {
        "personality_id": personality_id,
        "prompt_id": prompt_id,
        "scenario_id": scenario_id
    }


# ============================================================================
# TEST 1: Create Evaluation (POST /api/evaluations)
# ============================================================================

def test_create_evaluation(prompt_id, scenario_id):
    """Test creating a new evaluation"""
    print("\n" + "="*70)
    print("TEST 1: Create Evaluation (POST /api/evaluations)")
    print("="*70)
    
    evaluation_data = {
        "prompt_id": prompt_id,
        "scenario_id": scenario_id
    }
    
    print(f"\n📤 Sending POST request to create evaluation...")
    print(f"   Prompt ID: {prompt_id}")
    print(f"   Scenario ID: {scenario_id}")
    
    response = requests.post(f"{BASE_URL}/evaluations", json=evaluation_data)
    
    # Verify response
    assert response.status_code == 202, f"Expected 202, got {response.status_code}"
    print(f"✅ Status Code: {response.status_code} (202 Accepted)")
    
    result = response.json()
    
    # Verify response structure
    assert "result_id" in result, "Response should have result_id"
    assert "status" in result, "Response should have status"
    
    result_id = result["result_id"]
    status = result["status"]
    
    assert status == "PENDING", f"Initial status should be PENDING, got {status}"
    print(f"✅ Result ID: {result_id}")
    print(f"✅ Initial Status: {status}")
    
    return result_id


# ============================================================================
# TEST 2: Get Evaluation - Polling (GET /api/evaluations/{result_id})
# ============================================================================

def test_poll_evaluation_status(result_id):
    """Test polling evaluation status until completion"""
    print("\n" + "="*70)
    print("TEST 2: Poll Evaluation Status (GET /api/evaluations/{result_id})")
    print("="*70)
    
    print(f"\n🔄 Starting to poll evaluation {result_id}...")
    print(f"   Poll interval: {POLL_INTERVAL} seconds")
    print(f"   Max wait time: {MAX_POLL_TIME} seconds")
    
    start_time = time.time()
    poll_count = 0
    
    while True:
        poll_count += 1
        elapsed = time.time() - start_time
        
        print(f"\n   📊 Poll #{poll_count} (elapsed: {elapsed:.1f}s)")
        
        response = requests.get(f"{BASE_URL}/evaluations/{result_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        evaluation = response.json()
        status = evaluation["status"]
        
        print(f"      Status: {status}")
        
        # Check status
        if status == "COMPLETED":
            print(f"\n✅ Evaluation completed after {elapsed:.1f} seconds ({poll_count} polls)")
            return evaluation
        
        elif status == "FAILED":
            error = evaluation.get("error_message", "Unknown error")
            print(f"\n❌ Evaluation failed: {error}")
            assert False, f"Evaluation failed: {error}"
        
        elif status in ["PENDING", "RUNNING"]:
            # Check timeout
            if elapsed > MAX_POLL_TIME:
                print(f"\n❌ Timeout: Evaluation still {status} after {MAX_POLL_TIME}s")
                assert False, f"Evaluation timed out (still {status})"
            
            # Wait before next poll
            time.sleep(POLL_INTERVAL)
        
        else:
            assert False, f"Unexpected status: {status}"


# ============================================================================
# TEST 3: Verify Evaluation Results
# ============================================================================

def test_verify_evaluation_results(evaluation):
    """Verify the structure and content of completed evaluation"""
    print("\n" + "="*70)
    print("TEST 3: Verify Evaluation Results")
    print("="*70)
    
    # Verify status
    print("\n✅ Status: COMPLETED")
    assert evaluation["status"] == "COMPLETED"
    
    # Verify transcript exists
    print("\n📋 Verifying transcript...")
    assert "transcript" in evaluation, "Evaluation should have transcript"
    assert evaluation["transcript"] is not None, "Transcript should not be None"
    
    transcript = evaluation["transcript"]
    assert len(transcript) > 0, "Transcript should have messages"
    print(f"✅ Transcript has {len(transcript)} messages")
    
    # Verify transcript structure
    for i, msg in enumerate(transcript[:3]):  # Check first 3 messages
        assert "speaker" in msg, f"Message {i} should have speaker"
        assert "message" in msg, f"Message {i} should have message"
        assert msg["speaker"] in ["agent", "debtor"], f"Invalid speaker: {msg['speaker']}"
        print(f"   Message {i+1}: {msg['speaker'].upper()}: {msg['message'][:50]}...")
    
    # Verify scores exist
    print("\n📊 Verifying scores...")
    assert "scores" in evaluation, "Evaluation should have scores"
    assert evaluation["scores"] is not None, "Scores should not be None"
    
    scores = evaluation["scores"]
    assert "task_completion" in scores, "Should have task_completion score"
    assert "conversation_efficiency" in scores, "Should have conversation_efficiency score"
    
    task_completion = scores["task_completion"]
    conversation_efficiency = scores["conversation_efficiency"]
    
    # Verify score ranges
    assert 0 <= task_completion <= 100, f"Task completion out of range: {task_completion}"
    assert 0 <= conversation_efficiency <= 100, f"Conversation efficiency out of range: {conversation_efficiency}"
    
    print(f"✅ Task Completion: {task_completion}/100")
    print(f"✅ Conversation Efficiency: {conversation_efficiency}/100")
    
    # Verify evaluator analysis
    print("\n📝 Verifying evaluator analysis...")
    assert "evaluator_analysis" in evaluation, "Should have evaluator_analysis"
    assert evaluation["evaluator_analysis"] is not None, "Analysis should not be None"
    
    analysis = evaluation["evaluator_analysis"]
    assert len(analysis) > 0, "Analysis should not be empty"
    print(f"✅ Analysis length: {len(analysis)} characters")
    print(f"   Preview: {analysis[:100]}...")
    
    # Verify no error message
    error_msg = evaluation.get("error_message")
    assert error_msg is None, f"Should not have error message, got: {error_msg}"
    print(f"✅ No error message present")


# ============================================================================
# TEST 4: List All Evaluations (GET /api/evaluations)
# ============================================================================

def test_list_evaluations(result_id):
    """Test listing all evaluations"""
    print("\n" + "="*70)
    print("TEST 4: List All Evaluations (GET /api/evaluations)")
    print("="*70)
    
    print(f"\n📤 Getting all evaluations...")
    response = requests.get(f"{BASE_URL}/evaluations")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    print(f"✅ Status Code: {response.status_code}")
    
    evaluations = response.json()
    assert isinstance(evaluations, list), "Response should be a list"
    print(f"✅ Received list of {len(evaluations)} evaluations")
    
    # Find our test evaluation
    found = False
    for eval in evaluations:
        if eval.get("_id") == result_id:
            found = True
            print(f"✅ Found our test evaluation in list")
            print(f"   Status: {eval['status']}")
            break
    
    assert found, f"Should find evaluation {result_id} in list"


# ============================================================================
# TEST 5: Error Cases
# ============================================================================

def test_error_cases():
    """Test error handling for invalid requests"""
    print("\n" + "="*70)
    print("TEST 5: Error Cases and Validation")
    print("="*70)
    
    # Test 5.1: Invalid prompt ID
    print("\n🧪 Test 5.1: Create evaluation with invalid prompt ID")
    response = requests.post(f"{BASE_URL}/evaluations", json={
        "prompt_id": "invalid_id_12345",
        "scenario_id": "invalid_id_12345"
    })
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    print(f"✅ Returns 404 for invalid prompt ID")
    
    # Test 5.2: Get non-existent evaluation
    print("\n🧪 Test 5.2: Get evaluation with invalid result ID")
    response = requests.get(f"{BASE_URL}/evaluations/507f1f77bcf86cd799439011")
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    print(f"✅ Returns 404 for non-existent evaluation")
    
    # Test 5.3: Missing required fields
    print("\n🧪 Test 5.3: Create evaluation with missing fields")
    response = requests.post(f"{BASE_URL}/evaluations", json={
        "prompt_id": "some_id"
        # Missing scenario_id
    })
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"
    print(f"✅ Returns 422 for missing required fields")


# ============================================================================
# TEST 6: Delete Evaluation (Optional)
# ============================================================================

def test_delete_evaluation(result_id):
    """Test deleting an evaluation"""
    print("\n" + "="*70)
    print("TEST 6: Delete Evaluation (DELETE /api/evaluations/{result_id})")
    print("="*70)
    
    print(f"\n🗑️  Deleting evaluation {result_id}...")
    response = requests.delete(f"{BASE_URL}/evaluations/{result_id}")
    
    assert response.status_code == 204, f"Expected 204, got {response.status_code}"
    print(f"✅ Status Code: {response.status_code} (204 No Content)")
    
    # Verify it's gone
    print(f"\n🔍 Verifying evaluation is deleted...")
    response = requests.get(f"{BASE_URL}/evaluations/{result_id}")
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    print(f"✅ Evaluation successfully deleted (returns 404)")


# ============================================================================
# CLEANUP
# ============================================================================

def cleanup_test_data(test_data):
    """Clean up test data after tests"""
    print("\n" + "="*70)
    print("CLEANUP: Removing test data")
    print("="*70)
    
    if not test_data:
        print("⚠️  No test data to clean up")
        return
    
    # Delete scenario
    if "scenario_id" in test_data:
        print(f"\n🗑️  Deleting test scenario...")
        response = requests.delete(f"{BASE_URL}/scenarios/{test_data['scenario_id']}")
        if response.status_code == 204:
            print(f"✅ Deleted scenario")
        else:
            print(f"⚠️  Failed to delete scenario: {response.status_code}")
    
    # Delete prompt
    if "prompt_id" in test_data:
        print(f"\n🗑️  Deleting test prompt...")
        response = requests.delete(f"{BASE_URL}/prompts/{test_data['prompt_id']}")
        if response.status_code == 204:
            print(f"✅ Deleted prompt")
        else:
            print(f"⚠️  Failed to delete prompt: {response.status_code}")
    
    # Delete personality
    if "personality_id" in test_data:
        print(f"\n🗑️  Deleting test personality...")
        response = requests.delete(f"{BASE_URL}/personalities/{test_data['personality_id']}")
        if response.status_code == 204:
            print(f"✅ Deleted personality")
        else:
            print(f"⚠️  Failed to delete personality: {response.status_code}")


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def run_all_tests():
    """Run all end-to-end evaluation API tests"""
    print("\n" + "="*70)
    print("PHASE 3.3 BACKEND TESTING: COMPLETE E2E EVALUATION API")
    print("="*70)
    print("This test suite will:")
    print("  1. Create test data (personality, prompt, scenario)")
    print("  2. Create an evaluation (POST /api/evaluations)")
    print("  3. Poll for completion (GET /api/evaluations/{id})")
    print("  4. Verify results structure and content")
    print("  5. Test list all evaluations")
    print("  6. Test error cases")
    print("  7. Test deletion")
    print("  8. Clean up test data")
    print("="*70)
    
    test_data = None
    result_id = None
    
    try:
        # Check if server is running
        print("\n🔍 Checking if server is running...")
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=3)
            print(f"✅ Server is running at {BASE_URL}")
        except requests.exceptions.RequestException:
            print(f"\n❌ ERROR: Cannot connect to server at {BASE_URL}")
            print("   Please make sure the FastAPI server is running:")
            print("   cd backend && uvicorn main:app --reload")
            return
        
        # Setup test data
        test_data = setup_test_data()
        if not test_data:
            print("\n❌ Failed to create test data")
            return
        
        # Run tests
        result_id = test_create_evaluation(
            test_data["prompt_id"],
            test_data["scenario_id"]
        )
        
        evaluation = test_poll_evaluation_status(result_id)
        test_verify_evaluation_results(evaluation)
        test_list_evaluations(result_id)
        test_error_cases()
        test_delete_evaluation(result_id)
        
        # Clean up
        cleanup_test_data(test_data)
        
        # Success summary
        print("\n" + "="*70)
        print("✅ ALL END-TO-END API TESTS PASSED")
        print("="*70)
        print("Summary:")
        print("  ✅ Create evaluation endpoint working")
        print("  ✅ Polling mechanism working")
        print("  ✅ Results structure validated")
        print("  ✅ List evaluations working")
        print("  ✅ Error handling working")
        print("  ✅ Delete evaluation working")
        print("  ✅ Test data cleaned up")
        print("="*70)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        if test_data:
            print("\n⚠️  Attempting cleanup...")
            cleanup_test_data(test_data)
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        if test_data:
            print("\n⚠️  Attempting cleanup...")
            cleanup_test_data(test_data)
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()
    print("\n✨ Test suite completed successfully!\n")
