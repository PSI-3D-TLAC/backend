class PolozkaObjednavky:
    id: int
    quantity: int
    printQuality: str
    material: "Material"
    model: "Model3D"

    def __init__(self, id: int, quantity: int, printQuality: str, material: "Material" = None, model: "Model3D" = None):
        self.id = id
        self.quantity = quantity
        self.printQuality = printQuality
        self.material = material
        self.model = model
