import asyncio
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_full_pipeline():
    print("1. Testing Health & Root Endpoints...")
    r = client.get("/")
    assert r.status_code == 200, f"Root failed: {r.text}"
    print("   Root response:", r.json())

    r = client.get("/health")
    assert r.status_code == 200, f"Health failed: {r.text}"

    print("2. Testing User Registration...")
    reg_payload = {
        "name": "Alex Sharma",
        "email": "alex.test@spendwise.ai",
        "password": "Password123!",
    }
    r = client.post("/api/auth/register", json=reg_payload)
    print("   Register status:", r.status_code)
    assert r.status_code in (200, 201), f"Register failed: {r.text}"
    auth_data = r.json()
    token = auth_data["token"]
    assert token, "Token must be returned"
    print("   Token acquired:", token[:20] + "...")

    headers = {"Authorization": f"Bearer {token}"}

    print("3. Testing User Login...")
    r = client.post("/api/auth/login", json={"email": reg_payload["email"], "password": reg_payload["password"]})
    assert r.status_code == 200, f"Login failed: {r.text}"
    login_token = r.json()["token"]
    assert login_token

    print("4. Testing /api/auth/me...")
    r = client.get("/api/auth/me", headers=headers)
    assert r.status_code == 200, f"Me failed: {r.text}"
    print("   User profile:", r.json())

    print("5. Testing AI Categorization...")
    r = client.post("/api/ai/categorize", json={"text": "Zomato dinner delivery"})
    assert r.status_code == 200, f"Categorize failed: {r.text}"
    print("   Categorize result:", r.json())
    assert r.json()["category"] == "Food"

    r = client.post("/api/ai/categorize", json={"title": "Uber cab ride to airport"})
    assert r.status_code == 200
    assert r.json()["category"] == "Transport"

    print("6. Testing Expense Creation...")
    expense_data = {
        "title": "Starbucks Caramel Latte",
        "amount": 350.0,
        "category": "Food",
        "date": "2026-03-28",
        "payment_method": "UPI",
        "description": "Afternoon coffee break"
    }
    r = client.post("/api/expenses", json=expense_data, headers=headers)
    assert r.status_code in (200, 201), f"Create expense failed: {r.text}"
    created_expense = r.json()
    expense_id = created_expense["id"]
    print("   Created expense ID:", expense_id)

    print("7. Testing List Expenses...")
    r = client.get("/api/expenses", headers=headers)
    assert r.status_code == 200, f"List expenses failed: {r.text}"
    expenses_list = r.json()
    assert len(expenses_list) > 0
    print(f"   Found {len(expenses_list)} expenses")

    print("8. Testing Update Expense...")
    r = client.put(f"/api/expenses/{expense_id}", json={"amount": 380.0, "description": "Large Latte"}, headers=headers)
    assert r.status_code == 200, f"Update expense failed: {r.text}"
    assert r.json()["amount"] == 380.0

    print("9. Testing Budget Upsert & List...")
    budget_data = {"category": "Food", "limit": 6000.0}
    r = client.post("/api/budgets", json=budget_data, headers=headers)
    assert r.status_code == 200, f"Upsert budget failed: {r.text}"
    print("   Upserted budget:", r.json())

    r = client.get("/api/budgets", headers=headers)
    assert r.status_code == 200, f"List budgets failed: {r.text}"
    assert len(r.json()) > 0

    print("10. Testing AI Insights...")
    r = client.post("/api/ai/insights", headers=headers)
    assert r.status_code == 200, f"AI insights failed: {r.text}"
    insights = r.json()
    print("   Insights generated:", len(insights.get("insights", [])))

    print("11. Testing AI Chat...")
    r = client.post("/api/ai/chat", json={"question": "Where did I spend the most?"}, headers=headers)
    assert r.status_code == 200, f"AI chat failed: {r.text}"
    safe_answer = r.json()["answer"][:100].encode("ascii", "replace").decode("ascii")
    print("   AI Chat Answer:", safe_answer + "...")

    print("12. Testing Delete Expense...")
    r = client.delete(f"/api/expenses/{expense_id}", headers=headers)
    assert r.status_code == 200, f"Delete expense failed: {r.text}"

    print("\nALL BACKEND TESTS PASSED SUCCESSFULLY! PRODUCTION READY.")

if __name__ == "__main__":
    test_full_pipeline()
