
import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_root():
    """Test the root endpoint."""
    print(f"Testing root endpoint {BASE_URL}/...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Root endpoint is up.")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Is it running?")
        sys.exit(1)

def test_agent_query():
    """Test the agent query endpoint."""
    print("\nTesting /agent/query with 'Does garlic cure flu?'...")
    payload = {
        "query": "Does garlic cure flu?",
        "user_id": "test_user_1",
        "session_id": "session_1"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/agent/query", json=payload)
        if response.status_code == 200:
            data = response.json()
            print("✅ /agent/query successful.")
            
            # Verify Schema
            required_fields = ["final_answer", "verdict", "reasoning_trace", "evidence", "recommendations"]
            missing = [f for f in required_fields if f not in data]
            if missing:
                print(f"❌ Missing fields in response: {missing}")
            else:
                print(f"✅ Response Schema Valid. Verdict: {data['verdict']}")
                print(f"   Reasoning: {data['reasoning_trace']}")
        else:
            print(f"❌ /agent/query failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error testing /agent/query: {e}")

def test_memory():
    """Test memory retrieval."""
    print("\nTesting /memory endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/memory", params={"user_id": "test_user_1", "query": "garlic"})
        if response.status_code == 200:
            print(f"✅ /memory successful. Context retrieved.")
        else:
            print(f"❌ /memory failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing /memory: {e}")

def test_image_verdict():
    """Test that image queries return a True verdict."""
    print("\nTesting Image Verdict Logic...")
    payload = {
        "query": "Show me heart anatomy images",
        "user_id": "test_user_img",
        "session_id": "session_img"
    }
    try:
        response = requests.post(f"{BASE_URL}/agent/query", json=payload)
        data = response.json()
        if data['verdict'] == "True":
             print(f"✅ Image Verdict Logic Passed. Verdict: {data['verdict']}")
             print(f"   Response: {data['final_answer']}")
        else:
             print(f"❌ Image Verdict Logic Failed. Verdict: {data['verdict']}")
             print(f"   Debug Data: {json.dumps(data, indent=2)}")
    except Exception as e:
         print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_root()
    test_agent_query()
    test_image_verdict()
    test_memory()
