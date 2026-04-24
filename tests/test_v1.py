from app.core.decision_engine import DecisionEngine
from models.schemas import RouteRequest
from datetime import datetime


engine = DecisionEngine()


def run_test_case(name, request, expected_mode=None):
    print(f"\n=== {name} ===")
    res = engine.get_recommendation(request)

    print(f"Best Mode: {res.best_mode}")
    print(f"Explanation: {res.explanation}")

    for opt in res.options:
        print(f"- {opt.mode}: Score {opt.score}, Time {opt.time}m, Cost ₹{opt.cost}")

    # Assertion (if expected provided)
    if expected_mode:
        assert res.best_mode == expected_mode, \
            f"❌ Expected {expected_mode}, got {res.best_mode}"
        print("✅ Passed")


def test_all_cases():
    
    # 6. Extreme Traffic Scenario (Delhi Gate -> Gurgaon)
    run_test_case(
        "Delhi Gate to Gurugram (NCR Multi-modal)",
        RouteRequest(
            src=(28.64, 77.24),  # Delhi Gate Area
            dest=(28.45, 77.02), # Gurgaon Area
            time=datetime(2026, 4, 24, 18, 0)
        ),
        expected_mode="metro"
    )

    print("\n🎯 All tests executed!")


if __name__ == "__main__":
    test_all_cases()
