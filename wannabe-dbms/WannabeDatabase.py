import json
import os
from enum import Enum

from Loader import Loader, CLASS_REGISTRY


class WannabeDatabase:

    def __init__(self, loader: Loader = None):
        self.loader = loader if loader is not None else Loader()
        self.storage: dict = {}
        self._folder_path: str = None

    # ------------------------------------------------------------------ load
    def load(self, folder_path: str) -> None:

        self._folder_path = folder_path
        self.storage = self.loader.load_folder(folder_path)

    # ------------------------------------------------------------------ save
    def save(self) -> None:

        if self._folder_path is None:
            raise RuntimeError("Cannot save: database was never loaded from a folder")
        os.makedirs(self._folder_path, exist_ok=True)

        for class_name, bucket in self.storage.items():
            file_path = os.path.join(self._folder_path, f"{class_name}.json")
            items = [self._object_to_dict(obj) for obj in bucket.values()]
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(items, f, ensure_ascii=False, indent=2)

    # ------------------------------------------------------------------- get
    def get(self, class_name: str, id: int):

        bucket = self.storage.get(class_name)
        if bucket is None:
            return None
        return bucket.get(id)

    # ----------------------------------------------------------- put / helpers
    def put(self, class_name: str, obj) -> None:
        if class_name not in CLASS_REGISTRY:
            raise KeyError(f"Class '{class_name}' is not registered")
        bucket = self.storage.setdefault(class_name, {})
        obj_id = getattr(obj, "id", None)
        if obj_id is None:
            obj_id = len(bucket)
        bucket[obj_id] = obj

    @staticmethod
    def _object_to_dict(obj) -> dict:

        result = {}
        for key, value in vars(obj).items():
            if isinstance(value, Enum):
                result[key] = value.name
            elif hasattr(value, "id") and not isinstance(value, (int, float, str, bool)):
                result[key] = {"$ref": value.id}
            else:
                result[key] = value
        return result
