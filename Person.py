import json
from datetime import datetime

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
        self.ekg_tests = person_dict.get("ekg_tests", [])

    # Berechnet das Alter der Person
    def calculate_age(self):
        return datetime.today().year - int(self.date_of_birth)

    # Berechnet ob es sich um eine Risikoschwangerschaft handelt
    def is_high_risk_pregnancy(self):
        age = self.calculate_age()
        risk_conditions = ["Bluthochdruck", "Diabetes Typ 2"]

    # Bedingung 1: Alter über 35
        if age > 35:
            return True

    # Bedingung 2: Mehrlingsschwangerschaft
        if self.fetuses > 1:
            return True

    # Bedingung 3: Vorerkrankungen, die Risiko erhöhen
        for condition in self.medical_conditions:
            if condition in risk_conditions:
                return True

    # Wenn keine Bedingung zutrifft, ist es keine Risikoschwangerschaft
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
        """Hier wird die neue Datei geladen"""
        with open("data/person_db.json") as file:
            person_data = json.load(file)
        return person_data

    @staticmethod
    def get_person_list(person_data):
        """Gibt eine Liste aller Namen zurück"""
        list_of_names = []
        for eintrag in person_data:
            list_of_names.append(eintrag["lastname"] + ", " + eintrag["firstname"])
        return list_of_names

    @staticmethod
    def find_person_data_by_name(suchstring):
        person_data = Person.load_person_data()
        if suchstring == "None":
            return {}

        two_names = suchstring.split(", ")
        vorname = two_names[1]
        nachname = two_names[0]

        for eintrag in person_data:
            if (eintrag["lastname"] == nachname and eintrag["firstname"] == vorname):
                return eintrag
        else:
            return {}

if __name__ == "__main__":
    persons = Person.load_person_data()
    person_names = Person.get_person_list(persons)

    print("Verfügbare Personen:")
    print(person_names)
    print()

    # Beispiel: Eine Person suchen und ausgeben
    person_dict = Person.find_person_data_by_name("Klein, Sofia")
    if person_dict:
        person_obj = Person(person_dict)

        age = person_obj.calculate_age()
        print(f"Alter von {person_obj.firstname} {person_obj.lastname}: {age} Jahre")

        print(f"Vorerkrankungen: {person_obj.medical_conditions}")
        print(f"Anzahl Schwangerschaften: {person_obj.pregnancies}")
        print(f"Aktuelle Föten: {person_obj.fetuses}")
        print(f"CTG-Daten: {person_obj.ekg_tests}")

        if person_obj.is_high_risk_pregnancy():
            print("Die Schwangerschaft ist eine RISIKOSCHWANGERSCHAFT.")
        else:
            print("Die Schwangerschaft ist KEINE Risikoschwangerschaft.")
    else:
        print("Person nicht gefunden.")