import Zamestnanec

class Manazer(Zamestnanec.Zamestnanec):
    rola: int

    def __init__(self, id: int, name: str, email: str, password: str, dateOfBirht: str, rola: int):
        super().__init__(id, name, email, password, dateOfBirht)
        self.rola = rola

    def viewReports(self) -> list:
        return []

    def approveOrder(self, order) -> bool:
        return True

    def rejectOrder(self, order, reason: str) -> bool:
        return True

    def manageSuppliers(self, supplier) -> bool:
        return True
