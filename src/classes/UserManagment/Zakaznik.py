import Pouzivatel

class Zakaznik(Pouzivatel.Pouzivatel):
    address: str
    phone: str

    def __init__(self, id: int, name: str, email: str, password: str, dateOfBirht: str, address: str, phone: str):
        super().__init__(id, name, email, password, dateOfBirht)
        self.address = address
        self.phone = phone