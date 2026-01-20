import requests
import json
import sys

BASE_URL = "http://localhost:8001/api/v1"
EMAIL = "test@example.com"
PASSWORD = "password"

def run_test():
    print("--- Verifying History & Insights API ---")
    
    # 1. Login
    try:
        data = {"username": EMAIL, "password": PASSWORD}
        resp = requests.post(f"{BASE_URL}/auth/login", data=data) 
        if resp.status_code != 200:
            print(f"Login failed: {resp.text}")
            return
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("Login Success.")
    except Exception as e:
        print(f"Error connecting to API: {e}")
        return

    # 2. Run Query
    question = "Show 5 rows from livonia_cdb"
    print(f"Running Query: '{question}'...")
    try:
        # Assuming connection 2 exists and is valid from previous steps
        payload = {"question": question, "connection_id": 2}
        resp = requests.post(f"{BASE_URL}/query/nl", json=payload, headers=headers)
        
        if resp.status_code != 200:
            print(f"Query Failed: {resp.text}")
            return
            
        data = resp.json()
        print(f"Query Response Status: {resp.status_code}")
        
        # Check Insights
        insights = data.get("insights")
        query_id = data.get("query_id")
        
        if insights:
            print("✅ Insights Received:")
            print(json.dumps(insights, indent=2))
        else:
            print("❌ No insights in response!")
            
        if query_id:
             print(f"✅ Query ID: {query_id}")
        else:
             print("❌ No query_id in response!")
             
    except Exception as e:
        print(f"Query execution failed: {e}")
        return

    # 3. Check History
    print("\nFetching History...")
    try:
        resp = requests.get(f"{BASE_URL}/history/", headers=headers)
        if resp.status_code != 200:
             print(f"History Fetch Failed: {resp.text}")
             return
             
        history = resp.json()
        print(f"Found {len(history)} history items.")
        
        if len(history) > 0:
            latest = history[0]
            print(f"Latest Item ID: {latest['id']}")
            print(f"Latest Question: {latest['question']}")
            if latest['id'] == query_id:
                print("✅ Latest history item matches executed query ID.")
            else:
                print("❌ Mismatch in history ID.")
    except Exception as e:
        print(f"History verification failed: {e}")

if __name__ == "__main__":
    run_test()
