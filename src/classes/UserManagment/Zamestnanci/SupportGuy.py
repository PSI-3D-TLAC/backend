import Zamestnanec

class SupportGuy(Zamestnanec.Zamestnanec):
    def __init__(self, id: int, name: str, email: str, password: str, dateOfBirht: str):
        super().__init__(id, name, email, password, dateOfBirht)

    def handleRequest(self, request) -> bool:
        return True

    def resolveComplaint(self, complaint) -> bool:
        return True

    def rejectComplaint(self, complaint, reason: str) -> bool:
        return True

    def contactCustomer(self, customer, message: str) -> bool:
        return True
