import os
import unittest

from main import create_app


class ArsServerConformanceTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_capabilities_endpoint_shape(self):
        response = self.client.get("/capabilities")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIsInstance(payload, dict)
        self.assertEqual(payload.get("success"), True)
        self.assertIn("result", payload)
        result = payload["result"]
        self.assertIn("tools", result)
        self.assertIn("memory.build", result["tools"])

    def test_machine_readable_error_for_invalid_json_object(self):
        response = self.client.post("/memory", json=["not", "an", "object"])
        self.assertEqual(response.status_code, 400)
        payload = response.get_json()
        self.assertEqual(payload.get("success"), False)
        self.assertEqual(payload.get("error", {}).get("code"), "invalid_json")

    def test_reference_search_deterministic_matches(self):
        response_a = self.client.get("/reference/search?q=search&limit=3")
        response_b = self.client.get("/reference/search?q=search&limit=3")
        self.assertEqual(response_a.status_code, 200)
        self.assertEqual(response_b.status_code, 200)

        payload_a = response_a.get_json()
        payload_b = response_b.get_json()
        self.assertEqual(payload_a["result"]["query"], payload_b["result"]["query"])
        self.assertEqual(payload_a["result"]["limit"], payload_b["result"]["limit"])
        self.assertEqual(payload_a["result"]["matches"], payload_b["result"]["matches"])

    def test_optional_api_key_protection(self):
        original = os.environ.get("ARS_API_KEY")
        try:
            os.environ["ARS_API_KEY"] = "top-secret"
            no_key = self.client.post("/memory", json={"task": "t", "query": "q"})
            self.assertEqual(no_key.status_code, 401)
            no_key_payload = no_key.get_json()
            self.assertEqual(no_key_payload.get("error", {}).get("code"), "unauthorized")

            with_key = self.client.post(
                "/memory",
                json={"task": "t", "query": "q"},
                headers={"x-api-key": "top-secret"},
            )
            self.assertEqual(with_key.status_code, 200)
            with_key_payload = with_key.get_json()
            self.assertEqual(with_key_payload.get("success"), True)
        finally:
            if original is None:
                os.environ.pop("ARS_API_KEY", None)
            else:
                os.environ["ARS_API_KEY"] = original


if __name__ == "__main__":
    unittest.main()
