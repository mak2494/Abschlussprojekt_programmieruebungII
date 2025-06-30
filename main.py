import streamlit as st
from PIL import Image
from Person import Person  # Deine bestehende Person-Klasse
from datetime import datetime
import json
import os
from read_CSV import CTG_Data  # Deine CTG_Data-Klasse
from wehen_analysis import WehenAnalysis
from report_generator import generate_pdf
from ctg_simulator import CTGSimulator
import tempfile

st.set_page_config(page_title="CTG APP")

# ---------------------------------------------
# Tabs einrichten
# ---------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "👤 Person anzeigen",
    "📊 CTG Auswertung",
    "➕ Neue Person anlegen",
    "📄 PDF-Bericht",
    "▶️ Live-Simulation"
])
# ---------------------------------------------
# Tab 1: Person anzeigen & bearbeiten
# ---------------------------------------------
with tab1:
    st.title("CTG APP")
    st.write("## Versuchsperson auswählen")

    person_list_data = Person.load_person_data()
    person_names = Person.get_person_list(person_list_data)

    if 'current_user' not in st.session_state:
        st.session_state.current_user = 'None'

    st.session_state.current_user = st.selectbox(
        'Versuchsperson',
        options=['None'] + person_names,
        key="sbVersuchsperson"
    )

    if 'picture_path' not in st.session_state:
        st.session_state.picture_path = 'data/pictures/none.png'

    if st.session_state.current_user in person_names:
        selected_person_data = Person.find_person_data_by_name(st.session_state.current_user)
        selected_person = Person(selected_person_data)

        st.session_state.picture_path = selected_person.picture_path

        if os.path.exists(st.session_state.picture_path):
            image = Image.open(st.session_state.picture_path)
            st.image(image, caption=f"{selected_person.firstname} {selected_person.lastname}")
        else:
            st.warning("⚠️ Kein Bild gefunden oder Pfad ungültig.")

        st.write(f"*ID:* {selected_person.id}")
        st.write(f"*Alter:* {selected_person.calculate_age()} Jahre")
        st.write(f"*Geschlecht:* {selected_person.gender}")
        st.write(f"*Vorerkrankungen:* {', '.join(selected_person.medical_conditions) if selected_person.medical_conditions else 'Keine'}")
        st.write(f"*Anzahl Schwangerschaften:* {selected_person.pregnancies}")
        st.write(f"*Anzahl Föten:* {selected_person.fetuses}")
        st.write(f"*Schwangerschaftswoche:* {selected_person.gestational_age_weeks}")

        if selected_person.is_high_risk_pregnancy():
            st.warning("⚠️ Risikoschwangerschaft!")
        else:
            st.success("✅ Keine Risikoschwangerschaft.")

        if selected_person.fetuses_list:
            fetus_names = [f.name for f in selected_person.fetuses_list]
            selected_fetus_name = st.selectbox("Wähle einen Fötus:", options=fetus_names)
            fetus = next((f for f in selected_person.fetuses_list if f.name == selected_fetus_name), None)
            if fetus:
                st.info(f"{fetus}")
        else:
            st.info("Keine Föten vorhanden.")

        with st.expander("🔧 Person bearbeiten"):
            with st.form("edit_person_form"):
                new_firstname = st.text_input("Vorname", value=selected_person.firstname)
                new_lastname = st.text_input("Nachname", value=selected_person.lastname)
                new_gender = st.selectbox("Geschlecht", ["weiblich", "männlich"], index=0 if selected_person.gender == "weiblich" else 1)
                new_birthdate = st.date_input("Geburtsdatum", value=selected_person.date_of_birth)
                new_pregnancies = st.number_input("Anzahl Schwangerschaften", value=selected_person.pregnancies, step=1)
                new_fetuses = st.number_input("Anzahl Föten", value=selected_person.fetuses, step=1)
                new_gest_age = st.number_input("Schwangerschaftswoche", value=selected_person.gestational_age_weeks, step=1)
                new_medical_conditions = st.text_area("Vorerkrankungen (Komma-getrennt)", value=", ".join(selected_person.medical_conditions))
                new_picture_path = st.text_input("Bildpfad", value=selected_person.picture_path)

                save_btn = st.form_submit_button("Änderungen speichern")

                if save_btn:
                    selected_person_data["firstname"] = new_firstname
                    selected_person_data["lastname"] = new_lastname
                    selected_person_data["gender"] = new_gender
                    selected_person_data["date_of_birth"] = new_birthdate.isoformat()
                    selected_person_data["pregnancies"] = int(new_pregnancies)
                    selected_person_data["fetuses"] = int(new_fetuses)
                    selected_person_data["gestational_age_weeks"] = int(new_gest_age)
                    selected_person_data["medical_conditions"] = [s.strip() for s in new_medical_conditions.split(",") if s.strip()]
                    selected_person_data["picture_path"] = new_picture_path

                    with open("data/person_db.json", "w") as f:
                        json.dump(person_list_data, f, indent=4)

                    st.success("Änderungen gespeichert! Bitte neu auswählen, um sie zu sehen.")

# ---------------------------------------------
# Tab 2: CTG Auswertung
# ---------------------------------------------
with tab2:
    if st.session_state.current_user in person_names:
        selected_person_data = Person.find_person_data_by_name(st.session_state.current_user)
        selected_person = Person(selected_person_data)

        if selected_person.fetuses_list:
            fetus_names = [f.name for f in selected_person.fetuses_list]
            selected_fetus_name = st.selectbox("Fötus für HF-Auswertung wählen:", options=fetus_names, key="ctg_fetus_select")
        else:
            selected_fetus_name = None

        if selected_person.CTG_tests:
            selected_ctg_path = selected_person.CTG_tests[0]['result_link']
            ctg = CTG_Data(selected_ctg_path, fetus=selected_fetus_name)
            ctg.read_csv()

            avg_hr = ctg.average_HR_baby()
            max_hr = ctg.max_HR_baby()
            min_hr = ctg.min_HR_baby()

            st.write("### Fötus-Herzfrequenz-Auswertung")
            st.metric("Durchschnittliche HF", f"{avg_hr:.1f} bpm")
            st.metric("Maximale HF", f"{max_hr:.1f} bpm")
            st.metric("Minimale HF", f"{min_hr:.1f} bpm")

            st.write("### CTG-Diagramm")
            st.plotly_chart(ctg.plotly_figure(), use_container_width=True)

             # --- WEHEN-ANALYSE ---
            st.write("### Wehen-Abstand und -Dauer")
            # Parameter mit Slidern einstellbar machen
            min_height = st.slider("Minimale UC-Höhe", 0.0, 50.0, 5.0, key="wehen_height")
            min_distance = st.slider("Minimaler Abstand zwischen Wehen (s)", 5, 300, 120, key="wehen_distance")

            # Analyse-Objekt erzeugen
            wehen = WehenAnalysis(ctg)
            df_peaks = wehen.detect_contractions(height=min_height, distance=min_distance)
            df_cat   = wehen.classify_contractions(df_peaks)

            st.subheader("Erkannte Wehen")
            st.dataframe(df_cat, hide_index=True)

            # Zusammenfassung: Anzahl pro Kategorie
            summary = df_cat['category'].value_counts().rename_axis('Kategorie').reset_index(name='Anzahl')
            st.subheader("Anzahl Wehen pro Kategorie")
            st.table(summary)
            # ------------------------
        else:
            st.warning("⚠️ Keine CTG-Dateien für diese Person hinterlegt.")
    else:
        st.info("Bitte im ersten Tab eine Person auswählen.")

           

# ---------------------------------------------
# Tab 3: Neue Person anlegen
# ---------------------------------------------
with tab3:
    st.write("## ➕ Neue Person anlegen")

    with st.form("new_person_form"):
        new_id = st.text_input("ID")
        new_firstname = st.text_input("Vorname")
        new_lastname = st.text_input("Nachname")
        new_gender = st.selectbox("Geschlecht", ["weiblich", "männlich", "divers"])
        birth_date = st.date_input("Geburtsdatum")
        new_pregnancies = st.number_input("Anzahl Schwangerschaften", value=0, step=1)
        new_fetuses = st.number_input("Anzahl Föten", value=0, step=1)
        new_gest_age = st.number_input("Schwangerschaftswoche", value=0, step=1)
        new_medical_conditions = st.text_area("Vorerkrankungen (Komma-getrennt)")
        new_picture_path = st.text_input("Bildpfad", value="data/pictures/none.png")
        uploaded_csv = st.file_uploader("CTG/ CTG CSV-Datei hochladen", type=["csv"])

        add_btn = st.form_submit_button("Neue Person speichern")

        if add_btn:
            if any(p["id"] == new_id for p in person_list_data):
                st.error("ID existiert bereits!")
            else:
                ctg_dir = "data/CTG_data"
                os.makedirs(ctg_dir, exist_ok=True)

                ctg_tests = []
                if uploaded_csv is not None:
                    csv_path = os.path.join(ctg_dir, f"{new_id}.csv")
                    with open(csv_path, "wb") as f:
                        f.write(uploaded_csv.getbuffer())

                    ctg_tests.append({
                        "id": int(new_id),
                        "date": datetime.now().strftime("%d.%m.%Y"),
                        "result_link": csv_path
                    })
                new_person = {
                    "id": new_id,
                    "firstname": new_firstname,
                    "lastname": new_lastname,
                    "gender": new_gender,
                    "date_of_birth": birth_date.isoformat(),
                    "pregnancies": int(new_pregnancies),
                    "fetuses": int(new_fetuses),
                    "gestational_age_weeks": int(new_gest_age),
                    "medical_conditions": [s.strip() for s in new_medical_conditions.split(",") if s.strip()],
                    "picture_path": new_picture_path,
                    "CTG_tests": ctg_tests
                }

                person_list_data.append(new_person)
                with open("data/person_db.json", "w") as f:
                    json.dump(person_list_data, f, indent=4)

                st.success(f"Neue Person {new_firstname} {new_lastname} gespeichert!")
                if uploaded_csv is not None:
                    st.info(f"CSV gespeichert unter: {csv_path}")
                # 🔁 App neu laden, damit die neue Person im Dropdown erscheint
                st.rerun()


with tab4:
    st.write("## 📄 Bericht erstellen")

    if st.session_state.current_user in person_names:
        selected_person_data = Person.find_person_data_by_name(st.session_state.current_user)
        selected_person = Person(selected_person_data)

        st.write("### Inhalte für den PDF-Bericht auswählen:")

        include_info = st.checkbox("🧍 Basisdaten", value=True)
        include_risk = st.checkbox("⚠️ Risikoeinschätzung", value=True)
        include_ctg = st.checkbox("📊 CTG-Auswertung", value=True)
        include_image = st.checkbox("🖼 Profilbild in Bericht aufnehmen", value=True)
        include_ctg_plot = st.checkbox("📈 CTG-Diagramm einfügen", value=True)

        if st.button("📥 Bericht generieren"):
            pdf = generate_pdf(
                selected_person,
                include_info=include_info,
                include_risk=include_risk,
                include_ctg=include_ctg,
                include_image=include_image,
                include_ctg_plot=include_ctg_plot
            )

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
                pdf.output(tmpfile.name)
                with open(tmpfile.name, "rb") as f:
                    st.download_button(
                        label="📄 Bericht herunterladen",
                        data=f,
                        file_name=f"Bericht_{selected_person.firstname}_{selected_person.lastname}.pdf",
                        mime="application/pdf"
                    )
 # Tab 5: Live-Simulation & Alarm
# ---------------------------------------------
with tab5:
    st.title("▶️ CTG Live-Simulation")

    if st.session_state.current_user in person_names:
        # Person auswählen
        selected_person_data = Person.find_person_data_by_name(st.session_state.current_user)
        selected_person = Person(selected_person_data)

        if not selected_person.CTG_tests:
            st.warning("⚠️ Keine CTG-Dateien für diese Person hinterlegt.")
        else:
            # Fötus-Auswahl (falls vorhanden)
            if selected_person.fetuses_list:
                fetus_names = [f.name for f in selected_person.fetuses_list]
                selected_fetus_name = st.selectbox(
                    "Fötus wählen", options=fetus_names, key="sim_fetus_select"
                )
            else:
                selected_fetus_name = None

            # CTG-Dateipfad
            selected_ctg_path = selected_person.CTG_tests[0]['result_link']


            # CTG-Daten kurz laden, um die LB-Spalte zu bestimmen
            ctg = CTG_Data(selected_ctg_path, fetus=selected_fetus_name)
            ctg.read_csv()
            lb_col = ctg.get_lb_column()

            # Parameter-Einstellungen
            bpm_thr = st.number_input(
                "Alarm-Schwelle (bpm)", min_value=60, max_value=160, value=110, step=1
            )
            interval = st.select_slider(
                "Simulationstempo (Sekunden pro Schritt)",
                options=[0.1, 0.5, 1.0, 2.0],
                value=1.0,
                key="sim_speed"
            )

            # Simulator starten
            simulator = CTGSimulator(
                csv_path=selected_ctg_path,
                lb_col=lb_col,
                bpm_threshold=bpm_thr,
                interval=interval
            )
            simulator.run()  # ruft intern run_live() auf
    else:
        st.info("Bitte im ersten Tab eine Person auswählen.")