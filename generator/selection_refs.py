import uuid
from dataclasses import dataclass
from typing import Optional


ALLOWED_SELECTION_NAMESPACES = {"volume", "surface", "point", "curve"}
SELECTION_ID_GROUPS = {
    "volume": "volume",
    "surface": "boundary",
    "point": "boundary",
    "curve": "curve",
}


@dataclass(frozen=True)
class SelectionRef:
    uuid: str
    namespace: str
    backend_id: int
    name: Optional[str] = None
    mesh_uuid: Optional[str] = None


class SelectionPool:
    def __init__(self):
        self._next_backend_id = {
            group: 1
            for group in set(SELECTION_ID_GROUPS.values())
        }

    def allocate(self, namespace, *, name=None, backend_id=None, mesh_uuid=None):
        if namespace not in ALLOWED_SELECTION_NAMESPACES:
            raise ValueError("unsupported selection namespace: %r" % namespace)

        id_group = SELECTION_ID_GROUPS[namespace]
        if backend_id is None:
            backend_id = self._next_backend_id[id_group]
        elif not isinstance(backend_id, int):
            raise TypeError("selection backend_id must be an int")
        elif backend_id < 1:
            raise ValueError("selection backend_id must be positive")

        self._next_backend_id[id_group] = max(
            self._next_backend_id[id_group],
            backend_id + 1,
        )

        return SelectionRef(
            uuid=str(uuid.uuid4()),
            namespace=namespace,
            backend_id=backend_id,
            name=name,
            mesh_uuid=mesh_uuid,
        )
