class Pouzivatel:
    id: int
    name: str
    email: str
    password: str
    dateOfBirht: str

    def __init__(self, id: int, name: str, email: str, password: str, dateOfBirht: str):
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.dateOfBirht = dateOfBirht

    def login(self, email: str, password: str) -> bool:
        return self.email == email and self.password == password

    def logout(self) -> bool:
        return True

    def changePassword(self, oldPassword: str, newPassword: str) -> bool:
        if self.password != oldPassword:
            return False
        self.password = newPassword
        return True

    def updateEmail(self, newEmail: str):
        self.email = newEmail