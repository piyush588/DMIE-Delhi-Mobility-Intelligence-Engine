import time
import requests
import random

URL = "http://localhost:8000/api/v1/recommend"

# Bases for different locations in Delhi/NCR
LOCATIONS = [
    {"name": "CP to Noida", "src": [28.6139, 77.2090], "dest": [28.5355, 77.3910]},
    {"name": "Hauz Khas to Gurgaon", "src": [28.5494, 77.2001], "dest": [28.4595, 77.0266]},
    {"name": "Rohini to Dwarka", "src": [28.7041, 77.1025], "dest": [28.5823, 77.0500]},
    {"name": "Janakpuri to Saket", "src": [28.6219, 77.0878], "dest": [28.5244, 77.2066]},
    {"name": "Mayur Vihar to Karol Bagh", "src": [28.6046, 77.2949], "dest": [28.6550, 77.1888]}
]

def benchmark():
    latencies = []
    for loc in LOCATIONS:
        payload = {
            "src": loc["src"],
            "dest": loc["dest"],
            "time": "2026-04-25T10:00:00"
        }
        start = time.time()
        try:
            response = requests.post(URL, json=payload)
            end = time.time()
            if response.status_code == 200:
                latencies.append((end - start) * 1000)
                print(f"{loc['name']}: {latencies[-1]:.2f} ms")
            else:
                print(f"{loc['name']} failed: {response.status_code}")
        except Exception as e:
            print(f"{loc['name']} errored: {e}")
    
    if latencies:
        print(f"\nAverage Latency (Uncached): {sum(latencies)/len(latencies):.2f} ms")

if __name__ == "__main__":
    benchmark()
