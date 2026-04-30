import Pouzivatel

class Zakaznik(Pouzivatel.Pouzivatel):
    address: str
    phone: str

    def __init__(self, id: int, name: str, email: str, password: str, dateOfBirht: str, address: str, phone: str):
        super().__init__(id, name, email, password, dateOfBirht)
        self.address = address
        self.phone = phone

    def updateAddress(self, newAddress: str):
        self.address = newAddress

    def updatePhone(self, newPhone: str):
        self.phone = newPhone

    def createOrder(self, items: list) -> "Objednavka":
        from OrderManagment import Objednávka, StavObjednavky
        return Objednávka.Objednavka(0, StavObjednavky.StavObjednavky.VYTVORENA, "")

    def submitComplaint(self, reason: str) -> "Reklamacia":
        from Support import Reklamacia, StavReklamacie
        return Reklamacia.Reklamacia(0, reason, StavReklamacie.StavReklamacie.CREATED, "")