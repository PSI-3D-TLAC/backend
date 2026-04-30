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