import streamlit as st
from PIL import Image
from Person import Person  # Stelle sicher, dass deine Klasse in einer Datei `person.py` liegt!

st.write("# CTG APP")
st.write("## Versuchsperson auswählen")

# Lade die Personendaten
person_list = Person.load_person_data()
person_names = Person.get_person_list(person_list)

# Session State für aktuellen Benutzer
if 'current_user' not in st.session_state:
    st.session_state.current_user = 'None'

# Auswahlbox
st.session_state.current_user = st.selectbox(
    'Versuchsperson',
    options=person_names,
    key="sbVersuchsperson"
)

# Standard-Bild, wenn kein Name ausgewählt
if 'picture_path' not in st.session_state:
    st.session_state.picture_path = 'data/pictures/none.png'

# Wenn ein Benutzer ausgewählt wurde: Bild und Infos laden
if st.session_state.current_user in person_names:
    selected_person_data = Person.find_person_data_by_name(st.session_state.current_user)
    selected_person = Person(selected_person_data)

    st.session_state.picture_path = selected_person.picture_path

    # Bild anzeigen
    image = Image.open(st.session_state.picture_path)
    st.image(image, caption=f"{selected_person.firstname} {selected_person.lastname}")

    # Zusatzinfos
    st.write(f"**ID:** {selected_person.id}")
    st.write(f"**Alter:** {selected_person.calculate_age()} Jahre")
    st.write(f"**Vorerkrankungen:** {', '.join(selected_person.medical_conditions) if selected_person.medical_conditions else 'Keine'}")
    st.write(f"**Anzahl Schwangerschaften:** {selected_person.pregnancies}")
    st.write(f"**Föten:** {selected_person.fetuses}")

    # Risikoschwangerschaft anzeigen
    if selected_person.is_high_risk_pregnancy():
        st.warning("⚠️ Dies ist eine RISIKOSCHWANGERSCHAFT!")
    else:
        st.success("✅ Keine Risikoschwangerschaft.")

else:
    st.info("Bitte eine Versuchsperson auswählen.")