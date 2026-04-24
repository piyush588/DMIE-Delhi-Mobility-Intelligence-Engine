# Delhi Mobility Intelligence Engine (DMIE)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)

**DMIE** is an intelligent routing engine designed specifically for the complex urban landscape of Delhi. Unlike standard routing engines, DMIE uses **local intelligence**—peak hour patterns, metro proximity, and multi-modal heuristics—to recommend the *best* mode of transport, not just the shortest path.

---

## Key Features (V2 - Multi-modal Upgrade)

- **Smart Multi-modal Routing**: Automatically combines different modes (e.g., Auto -> Metro -> Auto) to find the absolute best way through NCR.
- **Dynamic Last-Mile Intelligence**: Calculates "hub" proximity and automatically links source/destination to the nearest metro stations.
- **Route Mode Comparison**: Compare Cab, Auto, Metro (multimodal), and Walking in a single call.
- **Peak Hour Intelligence**: Automatic traffic penalty/bonus applying during Delhi's rush hours (8-11 AM, 5-9 PM).
- **Weighted Scoring Engine**: A flexible algorithm that balances **Time, Cost, Comfort, and Reliability**.

---

## Tech Stack

- **Backend**: Python + FastAPI
- **Routing**: [OpenRouteService](https://openrouteservice.org/) integration
- **Database**: MongoDB (Geospatial querying)
- **Data**: Delhi Metro Open Data (DMRC)

---

## Quick Start

### 1. Clone & Install
```bash
git clone https://github.com/piyush588/DMIE-Delhi-Mobility-Intelligence-Engine.git
cd DMIE-Delhi-Mobility-Intelligence-Engine
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file from the example:
```bash
cp .env.example .env
```
*(Optional: Add your `ORS_API_KEY` for real-world traffic data)*

### 3. Run the Engine
```bash
python main.py
```

### 4. Test it (V2 Example)
```bash
curl -X POST "http://localhost:8000/api/v1/recommend" \
     -H "Content-Type: application/json" \
     -d '{
       "src": [28.64, 77.24],
       "dest": [28.45, 77.02],
       "time": "2026-04-24T18:00:00"
     }'
```

### 5. API Response Structure
The engine now returns a `segments` array for journey planning:
```json
{
  "best_mode": "metro",
  "confidence": 0.693,
  "explanation": "Metro recommended due to heavy traffic and hub proximity.",
  "options": [
    {
      "mode": "metro",
      "is_multimodal": true,
      "segments": [
        { "mode": "auto", "from_loc": "Source", "to_loc": "Karol Bagh", "duration_min": 5.5 },
        { "mode": "metro", "from_loc": "Karol Bagh", "to_loc": "HUDA City Centre", "duration_min": 45.0 },
        { "mode": "auto", "from_loc": "HUDA City Centre", "to_loc": "Destination", "duration_min": 21.0 }
      ]
    }
  ]
}
```

---

## How it Works (Scoring Logic)

DMIE calculates a **Mobility Score (0-1)** for every mode:
```python
score = (w_time * n_time) + (w_cost * n_cost) + (w_comfort * comfort) + (w_rel * reliability)
```
- **During Peak Hours**: Road modes (Cab/Auto) receive a `0.6x` time penalty.
- **Within 800m of Metro**: Metro receives a comfort and reliability bonus.

---

## Roadmap

- [x] **V2**: Multi-modal routing (e.g., Metro + Auto combinations).
- [ ] **V3**: Reliability indexing based on historic traffic trends.
- [ ] **V3**: Live Weather integration (Rain -> Cab preference).
- [ ] **V4**: Learning system to store and improve recommendations based on user choices.

---

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
