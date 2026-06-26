import unittest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from db import init_db
from event_replay_service import increment_tick, get_replay_status
from operational_engines import solve_voyage_plan
from observability_service import get_system_health

class TestOperationalSprints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize test DB tables
        init_db()
        from db import get_db_connection
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("DELETE FROM event_ledger")
        conn.commit()
        conn.close()

    def test_deterministic_replay(self):
        # Tick 1
        res1 = increment_tick()
        self.assertIn("correlation_id", res1)
        self.assertIn("audit_hash", res1)

        # Tick 2
        res2 = increment_tick()
        self.assertIn("correlation_id", res2)
        self.assertNotEqual(res1["audit_hash"], res2["audit_hash"])

        # History
        status = get_replay_status()
        self.assertIn("logs", status)
        self.assertTrue(len(status["logs"]) >= 2)

    def test_voyage_planning(self):
        # Test routing and draft validation
        res = solve_voyage_plan("patna", "varanasi", 2.2, "Bulk Carrier", 1500)
        
        self.assertTrue(res["is_feasible"])
        self.assertIn("recommended_path", res)
        self.assertIn("points_checked", res)
        
        # Test draft violation (Assuming draft > 3.0 fails for this route)
        res2 = solve_voyage_plan("kanpur", "patna", 3.5, "Tanker", 2000)
        self.assertFalse(res2["is_feasible"])
        self.assertTrue(len(res2["constraints_breached"]) > 0)

    def test_health_endpoint(self):
        health = get_system_health()
        self.assertEqual(health["status"], "healthy")
        self.assertEqual(health["database_status"], "connected")
        self.assertIn("system_health_score", health)

if __name__ == "__main__":
    unittest.main()
