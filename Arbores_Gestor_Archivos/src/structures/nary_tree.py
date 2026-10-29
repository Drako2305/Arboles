from collections import deque
from src.models.tree_node import TreeNode

class TreeError(ValueError):
    """Raised when a tree operation violates a structural rule."""

class NaryTree:
    """A manually implemented n-ary tree for a simulated file system."""

    def __init__(self, root_name="Mi unidad"):
        self.root = TreeNode(root_name, "folder")

    @staticmethod
    def validate_name(name):
        if not isinstance(name, str) or not name.strip():
            raise TreeError("El nombre no puede estar vacío.")
        clean = name.strip()
        if clean in {".", ".."} or "/" in clean or "\\" in clean:
            raise TreeError("El nombre contiene caracteres no permitidos.")
        return clean

    def find_by_id(self, node_id):
        if not node_id:
            return None
        for node in self.depth_first():
            if node.node_id == node_id:
                return node
        return None

    def find_by_name(self, name):
        target = (name or "").casefold()
        return [node for node in self.depth_first() if node.name.casefold() == target]

    def add_node(self, parent_id, name, node_type):
        name = self.validate_name(name)
        if node_type not in {"folder", "file"}:
            raise TreeError("El tipo debe ser carpeta o archivo.")
        parent = self.find_by_id(parent_id)
        if parent is None:
            raise TreeError("No se encontró la carpeta de destino.")
        if parent.node_type != "folder":
            raise TreeError("No se pueden crear elementos dentro de un archivo.")
        if any(child.name.casefold() == name.casefold() for child in parent.children):
            raise TreeError("Ya existe un elemento con ese nombre en esta carpeta.")
        node = TreeNode(name, node_type)
        parent.add_child(node)
        return node

    def rename_node(self, node_id, new_name):
        node = self.find_by_id(node_id)
        if node is None:
            raise TreeError("No se encontró el elemento.")
        if node is self.root:
            raise TreeError("No se puede renombrar la raíz.")
        name = self.validate_name(new_name)
        if any(child is not node and child.name.casefold() == name.casefold()
               for child in node.parent.children):
            raise TreeError("Ya existe un elemento con ese nombre en esta carpeta.")
        node.name = name
        return node

    def delete_node(self, node_id):
        node = self.find_by_id(node_id)
        if node is None:
            raise TreeError("No se encontró el elemento.")
        if node is self.root:
            raise TreeError("No se puede eliminar la raíz.")
        node.parent.children.remove(node)
        node.parent = None

    def move_node(self, node_id, new_parent_id):
        node = self.find_by_id(node_id)
        new_parent = self.find_by_id(new_parent_id)
        if node is None or new_parent is None:
            raise TreeError("No se encontró el elemento o la carpeta de destino.")
        if node is self.root:
            raise TreeError("No se puede mover la raíz.")
        if new_parent.node_type != "folder":
            raise TreeError("El destino debe ser una carpeta.")
        if node is new_parent or self.is_descendant(new_parent, node):
            raise TreeError("La operación generaría un ciclo.")
        if any(child.name.casefold() == node.name.casefold() for child in new_parent.children):
            raise TreeError("Ya existe un elemento con ese nombre en el destino.")
        node.parent.children.remove(node)
        new_parent.add_child(node)

    @staticmethod
    def is_descendant(candidate, ancestor):
        current = candidate
        while current is not None:
            if current is ancestor:
                return True
            current = current.parent
        return False

    def depth_first(self):
        result, stack = [], [self.root]
        while stack:
            node = stack.pop()
            result.append(node)
            stack.extend(reversed(node.children))
        return result

    def breadth_first(self):
        result, queue = [], deque([self.root])
        while queue:
            node = queue.popleft()
            result.append(node)
            queue.extend(node.children)
        return result

    def level(self, node):
        depth, current = 1, node
        while current.parent is not None:
            depth += 1
            current = current.parent
        return depth

    def height(self, node=None):
        node = node or self.root
        if not node.children:
            return 1
        return 1 + max(self.height(child) for child in node.children)

    def degree(self, node):
        return len(node.children)

    def max_degree(self):
        return max((self.degree(node) for node in self.depth_first()), default=0)

    def leaf_nodes(self):
        return [node for node in self.depth_first() if not node.children]

    def branch_nodes(self):
        return [node for node in self.depth_first() if node.children and node is not self.root]

    def weight(self):
        return len(self.depth_first())

    def to_dict(self):
        return self.root.to_dict()

    @classmethod
    def from_dict(cls, data):
        tree = cls(data["name"])
        tree.root = TreeNode.from_dict(data)
        if tree.root.node_type != "folder":
            raise TreeError("La raíz debe ser una carpeta.")
        return tree
