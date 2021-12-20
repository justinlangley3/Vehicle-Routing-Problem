class Package:
    package_id: int
    street: str
    city: str
    state: str
    postal: str
    deadline: str
    mass: int
    notes: str

    def __init__(self, package_id, street, city, state, postal, deadline, mass, notes):
        self.package_id = package_id
        self.street = street
        self.city = city
        self.state = state
        self.postal = postal
        self.deadline = deadline
        self.mass = mass
        self.notes = notes

    @property
    def package_id(self):
        return self.package_id

    @package_id.setter
    def package_id(self, package_id):
        self.package_id = package_id

    @property
    def street(self):
        return self.street

    @street.setter
    def street(self, street):
        self.street = street

    @property
    def city(self):
        return self.city

    @city.setter
    def city(self, city):
        self.city = city

    @property
    def state(self):
        return self.state

    @state.setter
    def state(self, state):
        self.state = state

    @property
    def postal(self):
        return self.postal

    @postal.setter
    def postal(self, postal):
        self.postal = postal

    @property
    def deadline(self):
        return self.deadline

    @deadline.setter
    def deadline(self, deadline):
        self.deadline = deadline

    @property
    def mass(self):
        return self.mass

    @mass.setter
    def mass(self, mass):
        self.mass = mass

    @property
    def notes(self):
        return self.notes

    @notes.setter
    def notes(self, notes):
        self.notes = notes
