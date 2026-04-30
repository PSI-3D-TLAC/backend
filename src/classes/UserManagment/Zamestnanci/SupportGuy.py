import Zamestnanec


class SupportGuy(Zamestnanec.Zamestnanec):
    def __init__(self, id: int, name: str, email: str, password: str, dateOfBirht: str):
        super().__init__(id, name, email, password, dateOfBirht)
