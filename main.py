import streamlit as st
from PIL import Image
from Person import Person  # Deine bestehende Person-Klasse mit Fetus-Klasse

st.write("# CTG APP")
st.write("## Versuchsperson auswählen")

# Lade Personendaten
person_list = Person.load_person_data()
person_names = Person.get_person_list(person_list)

# Session State für Benutzer
if 'current_user' not in st.session_state:
    st.session_state.current_user = 'None'

# Auswahlbox für Person
st.session_state.current_user = st.selectbox(
    'Versuchsperson',
    options=person_names,
    key="sbVersuchsperson"
)

# Platzhalter-Bild, wenn keine Person gewählt
if 'picture_path' not in st.session_state:
    st.session_state.picture_path = 'data/pictures/none.png'

# Wenn Person gewählt -> laden
if st.session_state.current_user in person_names:
    selected_person_data = Person.find_person_data_by_name(st.session_state.current_user)
    selected_person = Person(selected_person_data)

    st.session_state.picture_path = selected_person.picture_path

    # Bild anzeigen
    image = Image.open(st.session_state.picture_path)
    st.image(image, caption=f"{selected_person.firstname} {selected_person.lastname}")

    # ✅ BASISINFOS inkl. Schwangerschaftswoche
    st.write(f"**ID:** {selected_person.id}")
    st.write(f"**Alter:** {selected_person.calculate_age()} Jahre")
    st.write(f"**Vorerkrankungen:** {', '.join(selected_person.medical_conditions) if selected_person.medical_conditions else 'Keine'}")
    st.write(f"**Anzahl Schwangerschaften:** {selected_person.pregnancies}")
    st.write(f"**Anzahl Föten:** {selected_person.fetuses}")
    st.write(f"**Schwangerschaftswoche:** {selected_person.gestational_age_weeks}")

    # Risikoschwangerschaft
    if selected_person.is_high_risk_pregnancy():
        st.warning("⚠️ Dies ist eine RISIKOSCHWANGERSCHAFT!")
    else:
        st.success("✅ Keine Risikoschwangerschaft.")

    # 🎉 NEU: Fötus-Selectbox
    fetus_names = [f.name for f in selected_person.fetuses_list]

    if fetus_names:
        selected_fetus_name = st.selectbox(
            "Wähle einen Fötus:",
            options=fetus_names
        )

        # Hole ausgewählten Fötus
        selected_fetus = next((f for f in selected_person.fetuses_list if f.name == selected_fetus_name), None)

        if selected_fetus:
            st.info(f"**Ausgewählter Fötus:** {selected_fetus.name}")
            st.write(f"**Schwangerschaftswoche:** {selected_fetus.gestational_age_weeks}")
    else:
        st.info("Keine Föten vorhanden.")

else:
    st.info("Bitte eine Versuchsperson auswählen.")