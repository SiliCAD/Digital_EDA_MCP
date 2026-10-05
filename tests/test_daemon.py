import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from daemon import app
from src.clients.eda_client import EDADaemonClient

class TestDaemon(unittest.TestCase):
    def setUp(self):
        self.test_client = TestClient(app)

    def test_health_check(self):
        resp = self.test_client.get("/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["service"], "digital_eda_mcp_daemon")

    @patch("daemon.workboard")
    def test_workboard_endpoint(self, mock_workboard):
        mock_workboard.return_value = "WorkBoard status ok"
        resp = self.test_client.post("/workboard", json={"action": "status", "workboard_name": "default"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {"result": "WorkBoard status ok"})
        mock_workboard.assert_called_once()

    @patch("daemon.remote_control")
    def test_remote_control_endpoint(self, mock_remote):
        mock_remote.return_value = "Linux stdout"
        resp = self.test_client.post("/remote_control", json={"action": "run_command", "command": "uname -a"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {"result": "Linux stdout"})
        mock_remote.assert_called_once()

if __name__ == "__main__":
    unittest.main()
