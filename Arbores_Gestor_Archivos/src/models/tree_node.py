from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional
import uuid

@dataclass
class TreeNode:
    name: str
    node_type: str
    node_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    parent: Optional["TreeNode"] = field(default=None, repr=False)
    children: List["TreeNode"] = field(default_factory=list, repr=False)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def add_child(self, child: "TreeNode") -> None:
        child.parent = self
        self.children.append(child)

    def to_dict(self) -> dict:
        return {
            "id": self.node_id,
            "name": self.name,
            "type": self.node_type,
            "created_at": self.created_at,
            "children": [child.to_dict() for child in self.children],
        }

    @classmethod
    def from_dict(cls, data: dict, parent=None) -> "TreeNode":
        node = cls(
            name=data["name"],
            node_type=data["type"],
            node_id=data["id"],
            parent=parent,
            created_at=data.get("created_at", datetime.now(timezone.utc).isoformat()),
        )
        for child_data in data.get("children", []):
            node.add_child(cls.from_dict(child_data, node))
        return node
