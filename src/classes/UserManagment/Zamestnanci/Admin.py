import Zamestnanec

class Admin(Zamestnanec.Zamestnanec):
    def __init__(self, id: int, name: str, email: str, password: str, dateOfBirht: str):
        super().__init__(id, name, email, password, dateOfBirht)

    def addEmployee(self, employee: "Zamestnanec.Zamestnanec") -> bool:
        return True

    def removeEmployee(self, employeeId: int) -> bool:
        return True

    def resetPassword(self, user: "Zamestnanec.Zamestnanec", newPassword: str):
        user.password = newPassword

    def manageRoles(self, user: "Zamestnanec.Zamestnanec", role: str):
        pass
