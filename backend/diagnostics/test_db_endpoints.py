import os
import sys
import sqlite3
from fastapi.testclient import TestClient

# Ensure backend directory is in the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app
from database import DB_FILE, get_db_connection

client = TestClient(app)

def test_sqlite_db_exists():
    print("Testing DB File existence...")
    assert os.path.exists(DB_FILE), f"Database file does not exist at {DB_FILE}"
    print("✅ database.db exists!")

def test_db_structure():
    print("Testing DB schema structural integrity...")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row['name'] for row in cursor.fetchall()]
    print("Tables found in database:", tables)
    
    assert "predicted_emissions" in tables, "missing predicted_emissions table"
    assert "peak_alerts" in tables, "missing peak_alerts table"
    assert "cached_insights" in tables, "missing cached_insights table"
    
    # Check if rows are populated in predicted_emissions
    cursor.execute("SELECT COUNT(*) FROM predicted_emissions")
    pred_count = cursor.fetchone()[0]
    print(f"Number of predicted emissions rows: {pred_count}")
    assert pred_count > 0, "predicted_emissions table is empty"
    
    # Check peak alerts
    cursor.execute("SELECT COUNT(*) FROM peak_alerts")
    alert_count = cursor.fetchone()[0]
    print(f"Number of peak alerts generated: {alert_count}")
    
    conn.close()
    print("✅ DB schema and entries verified!")

def test_endpoints():
    print("Testing FastAPI endpoints using TestClient...")
    
    # 1. Test emissions endpoint
    response = client.get("/get-emissions/10")
    assert response.status_code == 200, f"Failed GET /get-emissions/10: {response.text}"
    data = response.json()
    assert "hour" in data and data["hour"] == 10
    assert "results" in data and len(data["results"]) > 0
    print("✅ GET /get-emissions/10 works!")
    print(f"   Example building total emission: {data['results'][0]['total_emission']} kg")
    
    # 2. Test alerts endpoint
    response = client.get("/get-alerts")
    assert response.status_code == 200, f"Failed GET /get-alerts: {response.text}"
    alerts = response.json()
    print(f"✅ GET /get-alerts works! Returned {len(alerts)} alerts.")
    if len(alerts) > 0:
        alert_id = alerts[0]['id']
        print(f"   First alert description: '{alerts[0]['alert_msg']}'")
        
        # 3. Test resolve alert
        resolve_response = client.post(f"/resolve-alert/{alert_id}")
        assert resolve_response.status_code == 200, f"Failed POST /resolve-alert/{alert_id}: {resolve_response.text}"
        print(f"✅ POST /resolve-alert/{alert_id} works!")
        
        # Verify resolved alert is not returned
        new_alerts_response = client.get("/get-alerts")
        new_alerts = new_alerts_response.json()
        assert not any(a['id'] == alert_id for a in new_alerts), "Alert was not resolved in output"
        print("✅ Alert resolution confirmed!")

if __name__ == "__main__":
    print("="*60)
    print("Backend SQLite & API Endpoint Diagnostics")
    print("="*60)
    try:
        test_sqlite_db_exists()
        test_db_structure()
        test_endpoints()
        print("\n🎉 ALL TESTS PASSED SUCCESSFULLY! Integration complete. 🎉")
    except AssertionError as ae:
        print(f"\n❌ TEST FAILED: {ae}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR RUNNING TESTS: {e}")
        sys.exit(1)
