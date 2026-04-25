import time
import requests

URL = "http://localhost:8000/api/v1/recommend"

# Short distance: CP to Janpath (approx 1km)
SHORT_LOC = {"name": "Short (CP to Janpath)", "src": [28.6289, 77.2190], "dest": [28.6250, 77.2210]}

def test_concurrency():
    payload = {
        "src": SHORT_LOC["src"],
        "dest": SHORT_LOC["dest"],
        "time": "2026-04-25T10:00:00"
    }
    start = time.time()
    response = requests.post(URL, json=payload)
    end = time.time()
    print(f"{SHORT_LOC['name']}: { (end - start) * 1000 :.2f} ms")
    print(f"Modes returned: {[opt['mode'] for opt in response.json()['options']]}")

if __name__ == "__main__":
    test_concurrency()
