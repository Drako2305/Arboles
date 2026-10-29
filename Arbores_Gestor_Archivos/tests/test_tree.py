import tempfile
import unittest
from pathlib import Path
from src.structures.nary_tree import NaryTree, TreeError
from src.services.file_service import FileService

class NaryTreeTests(unittest.TestCase):
    def setUp(self):
        self.tree = NaryTree("root")
        self.folder = self.tree.add_node(self.tree.root.node_id, "docs", "folder")
        self.file = self.tree.add_node(self.folder.node_id, "notes.txt", "file")

    def test_depth_first_and_breadth_first(self):
        self.assertEqual([n.name for n in self.tree.depth_first()], ["root", "docs", "notes.txt"])
        self.assertEqual([n.name for n in self.tree.breadth_first()], ["root", "docs", "notes.txt"])

    def test_metrics(self):
        self.assertEqual(self.tree.weight(), 3)
        self.assertEqual(self.tree.height(), 3)
        self.assertEqual(self.tree.level(self.file), 3)
        self.assertEqual(self.tree.degree(self.folder), 1)
        self.assertEqual(len(self.tree.leaf_nodes()), 1)

    def test_reject_file_parent(self):
        with self.assertRaises(TreeError):
            self.tree.add_node(self.file.node_id, "invalid", "file")

    def test_reject_duplicate_sibling(self):
        with self.assertRaises(TreeError):
            self.tree.add_node(self.folder.node_id, "NOTES.txt", "file")

    def test_reject_root_delete(self):
        with self.assertRaises(TreeError):
            self.tree.delete_node(self.tree.root.node_id)

    def test_reject_cycle(self):
        child = self.tree.add_node(self.folder.node_id, "nested", "folder")
        with self.assertRaises(TreeError):
            self.tree.move_node(self.folder.node_id, child.node_id)

    def test_move_node(self):
        destination = self.tree.add_node(self.tree.root.node_id, "other", "folder")
        self.tree.move_node(self.file.node_id, destination.node_id)
        self.assertIs(self.file.parent, destination)

    def test_rename(self):
        self.tree.rename_node(self.file.node_id, "updated.txt")
        self.assertEqual(self.file.name, "updated.txt")

    def test_delete_subtree(self):
        self.tree.delete_node(self.folder.node_id)
        self.assertEqual(self.tree.weight(), 1)

class PersistenceTests(unittest.TestCase):
    def test_json_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tree.json"
            service = FileService(path)
            service.create_node(service.tree.root.node_id, "Prueba", "folder")
            restored = FileService(path)
            self.assertIn("Prueba", [node.name for node in restored.tree.depth_first()])

if __name__ == "__main__":
    unittest.main()
