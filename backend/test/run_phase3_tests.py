"""
Phase 3.3 Backend Testing: Master Test Runner
Runs all Phase 3.3 test suites in sequence
"""

import sys
import os
import subprocess

# Test files to run in order
TEST_FILES = [
    "test_phase3_conversation_moderator.py",
    "test_phase3_transcript_evaluator.py",
    "test_phase3_complete_e2e.py"
]

TEST_DESCRIPTIONS = [
    "Conversation Moderator Tests (Mocked)",
    "Transcript Evaluator Tests (Mocked)",
    "Complete End-to-End API Tests (Real API)"
]


def run_test_file(filename, description):
    """Run a single test file and return success status"""
    print("\n" + "="*70)
    print(f"RUNNING: {description}")
    print(f"File: {filename}")
    print("="*70)
    
    try:
        # Run the test file
        result = subprocess.run(
            [sys.executable, filename],
            capture_output=False,
            text=True,
            cwd=os.path.dirname(__file__)
        )
        
        if result.returncode == 0:
            print(f"\n✅ {description} - PASSED")
            return True
        else:
            print(f"\n❌ {description} - FAILED")
            return False
            
    except Exception as e:
        print(f"\n❌ Error running {filename}: {e}")
        return False


def main():
    """Run all Phase 3.3 test suites"""
    print("\n" + "="*70)
    print("PHASE 3.3 BACKEND TESTING - MASTER TEST RUNNER")
    print("="*70)
    print("\nThis will run all Phase 3.3 test suites:")
    for i, desc in enumerate(TEST_DESCRIPTIONS, 1):
        print(f"  {i}. {desc}")
    print("\n" + "="*70)
    
    results = []
    
    # Run each test file
    for filename, description in zip(TEST_FILES, TEST_DESCRIPTIONS):
        success = run_test_file(filename, description)
        results.append((description, success))
    
    # Print summary
    print("\n" + "="*70)
    print("FINAL SUMMARY - PHASE 3.3 BACKEND TESTING")
    print("="*70)
    
    all_passed = True
    for description, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {description}")
        if not success:
            all_passed = False
    
    print("="*70)
    
    if all_passed:
        print("\n🎉 ALL PHASE 3.3 TESTS PASSED! 🎉")
        print("\nPhase 3.3 (Backend Testing) is now complete.")
        print("You can proceed to Phase 3.4 (Frontend Implementation).")
        print("\n" + "="*70)
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        print("\nPlease fix the failing tests before proceeding.")
        print("\n" + "="*70)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
