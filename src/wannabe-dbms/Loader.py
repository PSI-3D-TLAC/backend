import importlib.util
import json
import os
from enum import Enum


# Resolve the classes directory relative to this file.
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_CLASSES_DIR = os.path.normpath(os.path.join(_THIS_DIR, "../..", "src", "classes"))


# Registry: class_name -> (relative_file_path_inside_classes_dir, class_name_in_module)
# Values are paths from src/classes/. Slovak filenames with diacritics are kept
# exactly as they exist on disk.
CLASS_REGISTRY = {
    # Catalog
    "Produkt": ("Catalog/Produkt.py", "Produkt"),
    "Model3D": ("Catalog/Model3D.py", "Model3D"),
    # Inventory
    "Material": ("Inventory/Material.py", "Material"),
    # OrderManagment
    "Objednavka": ("OrderManagment/Objednávka.py", "Objednavka"),
    "PolozkaObjednavky": ("OrderManagment/PolozkaObjednávky.py", "PolozkaObjednavky"),
    "Tlaciaren": ("OrderManagment/Tlaciaren.py", "Tlaciaren"),
    "StavObjednavky": ("OrderManagment/StavObjednavky.py", "StavObjednavky"),
    "StavTlaciarne": ("OrderManagment/StavTlaciarne.py", "StavTlaciarne"),
    # Payment
    "Platba": ("Payment/Platba.py", "Platba"),
    "StavPlatby": ("Payment/StavPlatby.py", "StavPlatby"),
    # Delivery
    "Zasielka": ("Delivery/Zasielka.py", "Zasielka"),
    "Prepravca": ("Delivery/Prepravca.py", "Prepravca"),
    "TypDorucenia": ("Delivery/TypDorucenia.py", "TypDorucenia"),
    "StavZasielky": ("Delivery/StavZasielky.py", "StavZasielky"),
    # Support
    "Reklamacia": ("Support/Reklamacia.py", "Reklamacia"),
    "ZakaznickaPoziadavka": ("Support/ZakaznickaPoziadavka.py", "ZakaznickaPoziadavka"),
    "StavReklamacie": ("Support/StavReklamacie.py", "StavReklamacie"),
    "StavZakaznickejPoziadavky": ("Support/StavZakaznickejPoziadavky.py", "StavZakaznickejPoziadavky"),
    # SupplierIntegration
    "Dodavatel": ("SupplierIntegration/Dodavateľ.py", "Dodavatel"),
    # UserManagment
    "Pouzivatel": ("UserManagment/Pouzivatel.py", "Pouzivatel"),
    "Zakaznik": ("UserManagment/Zakaznik.py", "Zakaznik"),
    "Zamestnanec": ("UserManagment/Zamestnanci/Zamestnanec.py", "Zamestnanec"),
    "Admin": ("UserManagment/Zamestnanci/Admin.py", "Admin"),
    "Skladnik": ("UserManagment/Zamestnanci/Skladnik.py", "Sklaník"),
    "SupportGuy": ("UserManagment/Zamestnanci/SupportGuy.py", "SupportGuy"),
    "Manazer": ("UserManagment/Zamestnanci/Manazer.py", "Manazer"),
}


class Loader:
    """Loads python classes from src/classes and instantiates them from JSON data."""

    def __init__(self, classes_dir: str = _CLASSES_DIR):
        self.classes_dir = classes_dir
        self._class_cache: dict = {}

    def get_class(self, class_name: str):
        """Returns the python class object for a given registered class name."""
        if class_name in self._class_cache:
            return self._class_cache[class_name]

        if class_name not in CLASS_REGISTRY:
            raise KeyError(f"Class '{class_name}' is not registered in CLASS_REGISTRY")

        rel_path, internal_name = CLASS_REGISTRY[class_name]
        file_path = os.path.join(self.classes_dir, rel_path)

        # Build a unique, safe module name from the class name
        module_name = f"_wannabe_loaded_{class_name}"
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load module from {file_path}")
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except Exception:
            # Some class files use bare imports (e.g. `import StavPlatby`).
            # Fall back to extracting just the class definition by exec'ing
            # the file with the surrounding directory on sys.path.
            import sys
            dir_of_file = os.path.dirname(file_path)
            added = False
            if dir_of_file not in sys.path:
                sys.path.insert(0, dir_of_file)
                added = True
            try:
                spec.loader.exec_module(module)
            finally:
                if added:
                    sys.path.remove(dir_of_file)

        cls = getattr(module, internal_name)
        self._class_cache[class_name] = cls
        return cls

    def build_object(self, class_name: str, data: dict):
        """Instantiates an object of `class_name` using kwargs from `data`.

        Enum-typed fields (values that are strings matching enum members) are
        converted automatically when the constructor's annotations indicate an
        Enum subclass.
        """
        cls = self.get_class(class_name)
        kwargs = dict(data)

        # Convert string values to Enum members where the class annotation is an Enum
        annotations = getattr(cls, "__annotations__", {}) or {}
        # Include parent annotations
        for base in cls.__mro__[1:]:
            base_ann = getattr(base, "__annotations__", {}) or {}
            for k, v in base_ann.items():
                annotations.setdefault(k, v)

        for field, value in list(kwargs.items()):
            ann = annotations.get(field)
            if isinstance(ann, type) and issubclass(ann, Enum) and isinstance(value, str):
                kwargs[field] = ann[value] if value in ann.__members__ else ann(value)

        return cls(**kwargs)

    def load_folder(self, folder_path: str) -> dict:
        """Loads every <ClassName>.json file in `folder_path`.

        Each file should contain a JSON list of objects (dicts). Returns a dict:
            { class_name: { id: object, ... }, ... }
        """
        result: dict = {}
        if not os.path.isdir(folder_path):
            raise NotADirectoryError(f"{folder_path} is not a directory")

        for entry in sorted(os.listdir(folder_path)):
            if not entry.endswith(".json"):
                continue
            class_name = entry[:-len(".json")]
            if class_name not in CLASS_REGISTRY:
                # Skip unknown files silently
                continue

            full_path = os.path.join(folder_path, entry)
            with open(full_path, "r", encoding="utf-8") as f:
                items = json.load(f)

            class_bucket: dict = {}
            for item in items:
                obj = self.build_object(class_name, item)
                obj_id = getattr(obj, "id", None)
                if obj_id is None:
                    obj_id = len(class_bucket)
                class_bucket[obj_id] = obj
            result[class_name] = class_bucket

        return result
