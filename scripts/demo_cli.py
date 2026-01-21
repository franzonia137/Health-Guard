import requests
import sys
import time

API_URL = "http://localhost:8000"

def print_section(title):
    print("\n" + "="*40)
    print(f" {title}")
    print("="*40)

def wait_for_api():
    print("Checking if API is running (ensure 'make run-api' is running in another tab)...")
    # Actually, for this strict requirement "end-to-end runnable locally" and "make demo",
    # the user might expect this script to spin up the API too? 
    # Usually 'demo' assumes the service is reachable or self-contained. 
    # For simplicity, we assume the user follows 'make run-api' then 'make test-demo',
    # OR we can just import the agent directly if we want a standalone script without network.
    # Let's try network first, fallback to direct import if connection fails?
    # No, keep it clean: Network based to prove API works.
    try:
        requests.get(f"{API_URL}/docs", timeout=2)
        print("API is online!")
        return True
    except:
        print("API not reachable at localhost:8000. Please run 'make run-api' in a separate terminal!")
        return False

def run_query(user_id, session_id, query):
    print(f"\n>> USER: {query}")
    payload = {
        "user_id": user_id,
        "session_id": session_id,
        "query": query
    }
    try:
        resp = requests.post(f"{API_URL}/agent/query", json=payload)
        resp.raise_for_status()
        data = resp.json()
        print(f">> AGENT: {data['final_answer']}")
        print("\n   [Evidence Used]:")
        for item in data['evidence']:
            print(f"   - [{item['type']}] ({item['score']:.4f}) {item['content'][:100]}...")
        return data
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    print_section("Multimodal Misinformation Assistant - DEMO")
    
    if not wait_for_api():
        # Fallback for user convenience if they just ran 'python demo_cli.py' without server
        print("!! WARNING: Running in DIRECT MODE (No API) for demonstration purposes !!")
        from app.agent import MisinformationAgent
        from app.schemas import AgentQueryRequest
        agent = MisinformationAgent()
        
        def mock_send(u, s, q):
            print(f"\n>> USER: {q}")
            req = AgentQueryRequest(user_id=u, session_id=s, query=q)
            res = agent.process_query(req)
            print(f">> AGENT: {res.final_answer}")
            print("\n   [Evidence Used]:")
            for item in res.evidence:
                print(f"   - [{item.type}] ({item.score:.4f}) {item.content[:100]}...")
        
        user_id = "demo_user_1"
        session_id = "sess_01"
        
        mock_send(user_id, session_id, "Is the earth flat?")
        mock_send(user_id, session_id, "What did I just ask?")
        mock_send(user_id, session_id, "Do vaccines contain microchips?")
        
        return

    # API Mode
    user_id = "demo_user_web"
    session_id = "sess_web_01"

    print_section("Test Case 1: Check a Fake Claim")
    run_query(user_id, session_id, "Is it true that the earth is flat?")

    print_section("Test Case 2: Memory Recall")
    run_query(user_id, session_id, "what was the topic I asked about before?")

    print_section("Test Case 3: Multimodal / Image Retrieval")
    # This should trigger image search via CLIP
    run_query(user_id, session_id, "Show me images about 5G towers and viruses.")

if __name__ == "__main__":
    main()
