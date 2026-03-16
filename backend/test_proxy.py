import requests
import sys

def test_proxy():
    # Replace with local URL if testing locally, or the actual API base URL
    base_url = "https://pindownloader-gvif.onrender.com"
    # Using a known Pinterest video URL part or just testing the endpoint structure
    # Actually, let's just test the endpoint's response headers if we can
    
    # We can't easily test with a real Pinterest URL here because it might be dynamic,
    # but we can check if the endpoint exists and returns 422 (Unprocessable Entity) 
    # if parameters are missing, which confirms it's routed correctly.
    
    print(f"Testing proxy endpoint at {base_url}/api/proxy-download")
    
    try:
        response = requests.get(f"{base_url}/api/proxy-download", timeout=10)
        # It should return 422 because 'url' is required
        if response.status_code == 422:
            print("SUCCESS: Endpoint is alive and responding to requests.")
        else:
            print(f"WARNING: Unexpected status code {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"ERROR: Failed to connect to API: {e}")

if __name__ == "__main__":
    test_proxy()
