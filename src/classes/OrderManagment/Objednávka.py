import StavObjednavky

class Objednavka:
    id: int
    status: StavObjednavky.StavObjednavky
    createdAt: str

    def __init__(self, id: int, status: StavObjednavky.StavObjednavky, createdAt: str):
        self.id = id
        self.status = status
        self.createdAt = createdAt
        self.items: list = []

    def addItem(self, item):
        self.items.append(item)

    def removeItem(self, itemId: int) -> bool:
        for it in list(self.items):
            if getattr(it, "id", None) == itemId:
                self.items.remove(it)
                return True
        return False

    def calculateTotal(self) -> float:
        total = 0.0
        for it in self.items:
            price = getattr(getattr(it, "model", None), "volume", 0.0) or 0.0
            total += price * getattr(it, "quantity", 0)
        return total

    def updateStatus(self, newStatus: StavObjednavky.StavObjednavky):
        self.status = newStatus

    def confirm(self):
        self.status = StavObjednavky.StavObjednavky.POTVRDENA

    def cancel(self):
        self.status = StavObjednavky.StavObjednavky.ZRUSENA

    def complete(self):
        self.status = StavObjednavky.StavObjednavky.DOKONCENA
