import json
from pathlib import Path
from src.structures.nary_tree import NaryTree, TreeError

class FileService:
    def __init__(self, data_path=None):
        self.data_path = Path(data_path) if data_path else Path("data/tree.json")
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        self.tree = self._load_or_create()

    def _load_or_create(self):
        if self.data_path.exists():
            try:
                return NaryTree.from_dict(json.loads(self.data_path.read_text(encoding="utf-8")))
            except (json.JSONDecodeError, KeyError, TypeError, TreeError):
                pass
        tree = self._build_demo()
        self._save(tree)
        return tree

    @staticmethod
    def _build_demo():
        tree = NaryTree("Mi unidad")
        root = tree.root
        documents = tree.add_node(root.node_id, "Documentos", "folder")
        projects = tree.add_node(root.node_id, "Proyectos", "folder")
        media = tree.add_node(root.node_id, "Multimedia", "folder")
        tree.add_node(root.node_id, "Notas.txt", "file")
        university = tree.add_node(documents.node_id, "Universidad", "folder")
        tree.add_node(documents.node_id, "Hoja_de_vida.pdf", "file")
        tree.add_node(university.node_id, "Estructuras_de_datos", "folder")
        tree.add_node(university.node_id, "Bases_de_datos", "folder")
        tree.add_node(projects.node_id, "Insumap", "folder")
        tree.add_node(projects.node_id, "Gestor_Arboles", "folder")
        tree.add_node(media.node_id, "Imagenes", "folder")
        tree.add_node(media.node_id, "Presentacion.mp4", "file")
        tree.add_node(tree.find_by_name("Imagenes")[0].node_id, "Diagrama.png", "file")
        return tree

    def _save(self, tree=None):
        target = tree or self.tree
        self.data_path.write_text(json.dumps(target.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

    def create_node(self, parent_id, name, node_type):
        node = self.tree.add_node(parent_id, name, node_type)
        self._save()
        return node

    def rename_node(self, node_id, name):
        node = self.tree.rename_node(node_id, name)
        self._save()
        return node

    def delete_node(self, node_id):
        self.tree.delete_node(node_id)
        self._save()

    def move_node(self, node_id, parent_id):
        self.tree.move_node(node_id, parent_id)
        self._save()

    def reset_demo(self):
        self.tree = self._build_demo()
        self._save()

    def node_details(self, node):
        return {
            "id": node.node_id,
            "name": node.name,
            "type": node.node_type,
            "parent": node.parent.name if node.parent else None,
            "children": len(node.children),
            "degree": self.tree.degree(node),
            "level": self.tree.level(node),
            "is_leaf": not node.children,
            "path": self.path_of(node),
            "created_at": node.created_at,
        }

    @staticmethod
    def path_of(node):
        parts, current = [], node
        while current is not None:
            parts.append(current.name)
            current = current.parent
        return "/" + "/".join(reversed(parts))

    def get_tree_data(self):
        return self.tree.to_dict()

    def get_stats(self):
        nodes = self.tree.depth_first()
        folders = sum(node.node_type == "folder" for node in nodes)
        files = sum(node.node_type == "file" for node in nodes)
        return {
            "weight": self.tree.weight(),
            "folders": folders,
            "files": files,
            "leaves": len(self.tree.leaf_nodes()),
            "height": self.tree.height(),
            "max_degree": self.tree.max_degree(),
        }

    def search(self, query):
        term = (query or "").strip().casefold()
        if not term:
            return []
        return [self.node_details(node) for node in self.tree.depth_first()
                if term in node.name.casefold() or term in node.node_id.casefold()]

    def traversal(self, method):
        method = method.lower()
        if method == "dfs":
            nodes = self.tree.depth_first()
        elif method == "bfs":
            nodes = self.tree.breadth_first()
        else:
            raise ValueError("Recorrido no válido. Utiliza DFS o BFS.")
        return [{"id": node.node_id, "name": node.name, "type": node.node_type,
                 "level": self.tree.level(node)} for node in nodes]
