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

    def updateQuantity(self, quantity: int):
        self.quantity = quantity

    def setMaterial(self, material: "Material"):
        self.material = material

    def setModel(self, model: "Model3D"):
        self.model = model

    def setPrintQuality(self, quality: str):
        self.printQuality = quality

    def getSubtotal(self, unitPrice: float) -> float:
        return unitPrice * self.quantity
