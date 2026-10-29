import tempfile
import unittest
from pathlib import Path
from app import create_app

class ApiTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.app = create_app(Path(self.temp_dir.name) / "tree.json")
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_home(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_tree_and_stats(self):
        self.assertEqual(self.client.get("/api/tree").status_code, 200)
        self.assertIn("weight", self.client.get("/api/stats").get_json())

    def test_create_folder(self):
        root = self.client.get("/api/tree").get_json()
        response = self.client.post("/api/nodes", json={
            "parent_id": root["id"], "name": "Nueva carpeta", "type": "folder"
        })
        self.assertEqual(response.status_code, 201)

    def test_invalid_traversal(self):
        self.assertEqual(self.client.get("/api/traversal/invalid").status_code, 400)

if __name__ == "__main__":
    unittest.main()
