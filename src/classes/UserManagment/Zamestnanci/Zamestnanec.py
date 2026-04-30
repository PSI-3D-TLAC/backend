import Pouzivatel.Pouzivatel

class Zamestnanec(Pouzivatel.Pouzivatel):
    def __init__(self, id: int, name: str, email: str, password: str, dateOfBirht: str):
        super().__init__(id, name, email, password, dateOfBirht)

    def clockIn(self):
        pass

    def clockOut(self):
        pass

    def getRole(self) -> str:
        return self.__class__.__name__