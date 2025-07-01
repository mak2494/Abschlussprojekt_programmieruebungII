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
import pandas as pd
import time
import plotly.graph_objects as go
from streamlit.runtime.scriptrunner import RerunException


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
            # 💾 Für spätere Nutzung (z. B. Tab 4/PDF) speichern
            st.session_state.selected_fetus_name = selected_fetus_name
        else:
            selected_fetus_name = None
            st.session_state.selected_fetus_name = None

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

        # Fötus-Auswahl
        fetus_name = None
        if selected_person.fetuses_list:
            fetus_options = [f.name for f in selected_person.fetuses_list]
            fetus_name = st.selectbox("👶 Fötus für Bericht wählen", options=fetus_options)

        # Zeitbereichs-Auswahl (maximal 750 Sekunden)
        selected_time_range = None
        if include_ctg_plot:
            st.write("### Zeitbereich für Diagramm (Sekunden)")
            MAX_TIME = 740
            start_time = st.number_input("Startzeit (s)", min_value=0, max_value=MAX_TIME - 10, value=0, step=10)
            end_time = st.number_input(
                "Endzeit (s)", 
                min_value=start_time + 10, 
                max_value=MAX_TIME, 
                value=min(start_time + 300, MAX_TIME), 
                step=10
            )
            selected_time_range = (start_time, end_time)

        if st.button("📥 Bericht generieren"):
            pdf = generate_pdf(
                selected_person,
                include_info=include_info,
                include_risk=include_risk,
                include_ctg=include_ctg,
                include_image=include_image,
                include_ctg_plot=include_ctg_plot,
                fetus_name=fetus_name,
                time_range=selected_time_range
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
    else:
        st.info("Bitte im ersten Tab eine Person auswählen.")

# ---------------------------------------------
# Tab 5: Live-Simulation & Alarm mit Standbild
# ---------------------------------------------
with tab5:
    st.title("▶️ CTG Live-Simulation")

    # 1) Vorbedingungen
    if st.session_state.current_user not in person_names:
        st.info("Bitte im ersten Tab eine Person auswählen.")
        st.stop()
    person_data = Person.find_person_data_by_name(st.session_state.current_user)
    if not person_data["CTG_tests"]:
        st.warning("⚠️ Keine CTG-Dateien für diese Person hinterlegt.")
        st.stop()

    # 2) Fötus-Auswahl
    ctg_path = person_data["CTG_tests"][0]["result_link"]
    fetuses = Person(person_data).fetuses_list or []
    selected_fetus_name = None
    if fetuses:
        selected_fetus_name = st.selectbox(
            "Fötus wählen", [f.name for f in fetuses], key="sim_fetus_select"
        )

    # 3) Parameter
    bpm_thr  = st.number_input("Alarm-Schwelle (bpm)", 60, 160, 110, 1, key="sim_bpm_thr")
    interval = st.select_slider(
        "Simulations-Tempo (Sekunden pro Schritt)",
        [0.1, 0.5, 1.0, 2.0], 0.1, key="sim_interval"
    )

    # 4) Session-State für Start/Stop (einmalig)
    if "sim_running" not in st.session_state:
        st.session_state.sim_running = False
    if "sim_alerts" not in st.session_state:
        st.session_state.sim_alerts = []

    # 5) Buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ Start Simulation", key="btn_start_sim"):
            # Start: sim_running an und Alerts zurücksetzen
            st.session_state.sim_running = True
            st.session_state.sim_alerts = []
    with col2:
        if st.button("⏹️ Stop Simulation", key="btn_stop_sim"):
            st.session_state.sim_running = False

    # 6) Wenn gerade läuft: Simulation starten
    if st.session_state.sim_running:
        simulator = CTGSimulator(
            csv_path=ctg_path,
            lb_col=CTG_Data(ctg_path, fetus=selected_fetus_name).get_lb_column(),
            bpm_threshold=bpm_thr,
            interval=interval
        )
        simulator.run_live()

    # 7) Wenn gestoppt oder noch nie gestartet: letztes Standbild zeigen
    else:
        # letzte Figur?
        if "sim_last_fig" in st.session_state and st.session_state.sim_last_fig is not None:
            st.plotly_chart(st.session_state.sim_last_fig, use_container_width=True)
            # gespeicherte Alerts anzeigen
            if st.session_state.sim_alerts:
                st.warning("🔔 Alarm-Übersicht:")
                for alert in st.session_state.sim_alerts:
                    st.error(alert)
        else:
            st.info("Klicke ▶️ Start Simulation, um zu beginnen.")
