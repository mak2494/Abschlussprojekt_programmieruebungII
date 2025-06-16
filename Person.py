import json
from datetime import datetime


class Fetus:
    def __init__(self, name, gestational_age_weeks):
        self.name = name
        self.gestational_age_weeks = gestational_age_weeks

    def __str__(self):
        return f"Fötus: {self.name}, Schwangerschaftswoche: {self.gestational_age_weeks}"


class Person:
    def __init__(self, person_dict) -> None:
        self.date_of_birth = person_dict["date_of_birth"]
        self.firstname = person_dict["firstname"]
        self.lastname = person_dict["lastname"]
        self.picture_path = person_dict["picture_path"]
        self.id = person_dict["id"]
        self.gender = person_dict["gender"]
        self.medical_conditions = person_dict.get("medical_conditions", [])
        self.pregnancies = person_dict.get("pregnancies", 0)
        self.fetuses = person_dict.get("fetuses", 0)
        self.gestational_age_weeks = person_dict.get("gestational_age_weeks", 0)
        self.ekg_tests = person_dict.get("ekg_tests", [])

        # NEU: erstelle Liste mit echten Fetus-Objekten
        self.fetuses_list = []
        for i in range(1, self.fetuses + 1):
            fetus = Fetus(name=f"Fötus {i}", gestational_age_weeks=self.gestational_age_weeks)
            self.fetuses_list.append(fetus)

    # Berechnet das Alter der Person
    def calculate_age(self):
        return datetime.today().year - int(self.date_of_birth)

    # Prüft, ob es eine Risikoschwangerschaft ist
    def is_high_risk_pregnancy(self):
        age = self.calculate_age()
        risk_conditions = ["Bluthochdruck", "Diabetes Typ 2"]

        if age > 35:
            return True
        if self.fetuses > 1:
            return True
        for condition in self.medical_conditions:
            if condition in risk_conditions:
                return True
        return False

    # Pfad zum Bild der Person zurückgeben
    def get_picture_path(self):
        return self.picture_path

    @staticmethod
    def load_by_id(person_id):
        person_data = Person.load_person_data()
        for person in person_data:
            if person["id"] == person_id:
                return Person(person)
        return None

    @staticmethod
    def load_person_data():
        with open("data/person_db.json") as file:
            person_data = json.load(file)
        return person_data

    @staticmethod
    def get_person_list(person_data):
        return [f"{p['lastname']}, {p['firstname']}" for p in person_data]

    @staticmethod
    def find_person_data_by_name(suchstring):
        person_data = Person.load_person_data()
        if suchstring == "None":
            return {}
        two_names = suchstring.split(", ")
        vorname = two_names[1]
        nachname = two_names[0]
        for eintrag in person_data:
            if eintrag["lastname"] == nachname and eintrag["firstname"] == vorname:
                return eintrag
        return {}


if __name__ == "__main__":
    persons = Person.load_person_data()
    person_names = Person.get_person_list(persons)

    print("Verfügbare Personen:")
    print(person_names)
    print()

    # Beispiel: Eine Person suchen und anzeigen
    person_dict = Person.find_person_data_by_name("Klein, Sofia")
    if person_dict:
        person_obj = Person(person_dict)

        print(f"ID: {person_obj.id}")
        print(f"Name: {person_obj.firstname} {person_obj.lastname}")
        print(f"Alter: {person_obj.calculate_age()} Jahre")
        print(f"Vorerkrankungen: {person_obj.medical_conditions}")
        print(f"Anzahl Schwangerschaften: {person_obj.pregnancies}")
        print(f"Anzahl Föten: {person_obj.fetuses}")
        print(f"Schwangerschaftswoche: {person_obj.gestational_age_weeks}")
        print(f"CTG-Daten: {person_obj.ekg_tests}")

        # Föten ausgeben
        print("Föten:")
        for fetus in person_obj.fetuses_list:
            print(f"  - {fetus}")

        if person_obj.is_high_risk_pregnancy():
            print("⚠️ Dies ist eine RISIKOSCHWANGERSCHAFT!")
        else:
            print("✅ Keine Risikoschwangerschaft.")
    else:
        print("Person nicht gefunden.")