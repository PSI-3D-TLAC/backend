import Zamestnanec


class Manazer(Zamestnanec.Zamestnanec):
    rola: int

    def __init__(self, id: int, name: str, email: str, password: str, dateOfBirht: str, rola: int):
        super().__init__(id, name, email, password, dateOfBirht)
        self.rola = rola
