import json
from datetime import datetime


class Fetus:
    """Repräsentiert einen Fötus mit Name und Schwangerschaftswoche"""
    def __init__(self, name, gestational_age_weeks):
        """Initialisiert einen Fötus mit Namen und Schwangerschaftswoche"""
        self.name = name
        self.gestational_age_weeks = gestational_age_weeks

    def __str__(self):
        """Gibt eine lesbare Darstellung des Fötus zurück"""
        return f"Fötus: {self.name}, Schwangerschaftswoche: {self.gestational_age_weeks}"


class Person:
    """Repräsentiert eine schwangere Person mit medizinischen und persönlichen Daten"""
    def __init__(self, person_dict) -> None:
        """ Initialisiert ein Person-Objekt basierend auf einem Dictionary aus JSON-Daten"""
        self.date_of_birth = datetime.strptime(person_dict["date_of_birth"], "%Y-%m-%d")
        self.firstname = person_dict["firstname"]
        self.lastname = person_dict["lastname"]
        self.picture_path = person_dict["picture_path"]
        self.id = person_dict["id"]
        self.gender = person_dict["gender"]
        self.medical_conditions = person_dict.get("medical_conditions", [])
        self.pregnancies = person_dict.get("pregnancies", 0)
        self.fetuses = person_dict.get("fetuses", 0)
        self.gestational_age_weeks = person_dict.get("gestational_age_weeks", 0)
        self.CTG_tests = person_dict.get("CTG_tests", [])

        # NEU: erstelle Liste mit echten Fetus-Objekten
        self.fetuses_list = []
        for i in range(1, self.fetuses + 1):
            fetus = Fetus(name=f"Fötus {i}", gestational_age_weeks=self.gestational_age_weeks)
            self.fetuses_list.append(fetus)

    
    def calculate_age(self):
        """Berechnet das Alter der Person basierend auf dem Geburtsdatum"""
        today = datetime.today()
        age = today.year - self.date_of_birth.year
        if (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day):
            age -= 1
        return age
    

    def is_high_risk_pregnancy(self):
        """Bestimmt, ob es sich um eine Risikoschwangerschaft handelt"""
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

    
    def get_picture_path(self):
        """Gibt den Pfad zum Bild der Person zurück"""
        return self.picture_path

    @staticmethod
    def load_by_id(person_id):
        """Lädt eine Person basierend auf der ID aus der JSON-Datenbank"""
        person_data = Person.load_person_data()
        for person in person_data:
            if person["id"] == person_id:
                return Person(person)
        return None

    @staticmethod
    def load_person_data():
        """Lädt die Personendaten aus der JSON-Datei"""
        with open("data/person_db.json") as file:
            person_data = json.load(file)
        return person_data

    @staticmethod
    def get_person_list(person_data):
        """Erstellt eine Liste von Personennamen im Format 'Nachname, Vorname'"""
        return [f"{p['lastname']}, {p['firstname']}" for p in person_data]

    @staticmethod
    def find_person_data_by_name(suchstring):
        """Findet die Personendaten basierend auf dem Namen im Format 'Nachname, Vorname'"""
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
        print(f"CTG-Daten: {person_obj.CTG_tests}")

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