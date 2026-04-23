# 🧠 Delhi Mobility Intelligence Engine (DMIE)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)

**DMIE** is an intelligent routing engine designed specifically for the complex urban landscape of Delhi. Unlike standard routing engines, DMIE uses **local intelligence**—peak hour patterns, metro proximity, and multi-modal heuristics—to recommend the *best* mode of transport, not just the shortest path.

---

## 🚀 Key Features (V1)

- **Route Mode Comparison**: Compare Cab, Auto, Metro, and Walking in a single call.
- **Peak Hour Intelligence**: Automatic traffic penalty/bonus applying during Delhi's rush hours (8-11 AM, 5-9 PM).
- **Metro Proximity Detection**: Integrated database of 200+ Delhi Metro stations with automatic "last-mile" feasibility scoring.
- **Weighted Scoring Engine**: A flexible algorithm that balances **Time, Cost, Comfort, and Reliability**.
- **Mock Mode**: Functional out-of-the-box using distance heuristics even without external API keys.

---

## 🛠️ Tech Stack

- **Backend**: Python + FastAPI
- **Routing**: [OpenRouteService](https://openrouteservice.org/) integration
- **Database**: MongoDB (Geospatial querying)
- **Data**: Delhi Metro Open Data (DMRC)

---

## 🚦 Quick Start

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

### 4. Test it
```bash
curl -X POST "http://localhost:8000/api/v1/recommend" \
     -H "Content-Type: application/json" \
     -d '{
       "src": [28.6440, 77.1885],
       "dest": [28.5279, 77.2056],
       "time": "2026-04-24T18:00:00"
     }'
```

---

## 💡 How it Works (Scoring Logic)

DMIE calculates a **Mobility Score (0-1)** for every mode:
```python
score = (w_time * n_time) + (w_cost * n_cost) + (w_comfort * comfort) + (w_rel * reliability)
```
- **During Peak Hours**: Road modes (Cab/Auto) receive a `0.6x` time penalty.
- **Within 800m of Metro**: Metro receives a comfort and reliability bonus.

---

## 🗺️ Roadmap

- [ ] **V2**: Multi-modal routing (e.g., Metro + Auto combinations).
- [ ] **V2**: Reliability indexing based on historic traffic trends.
- [ ] **V2**: Live Weather integration (Rain -> Cab preference).
- [ ] **V3**: Learning system to store and improve recommendations based on user choices.

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
