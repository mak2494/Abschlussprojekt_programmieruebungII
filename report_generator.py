"""
generate_report.py

Dieses Modul erstellt PDF-Berichte zu CTG-Messungen und Personendaten.
Es unterstützt optionale Inhalte wie Basisdaten, Risikoeinschätzung,
Herzfrequenzanalysen, CTG-Diagramme und Wehenanalysen.
"""
import os
import tempfile
from fpdf import FPDF
from read_CSV import CTG_Data
from plotly.colors import qualitative
from wehen_analysis import WehenAnalysis
import pandas as pd
import plotly.io as pio

# Optional: sichere Start-Parameter für headless Chrome
pio.kaleido.scope.chromium_args = ["--no-sandbox", "--disable-dev-shm-usage"]

class PDF(FPDF):
    """
    Erweiterte FPDF-Klasse mit Kopf- und Fußzeile für CTG-Berichte.
    """
    def header(self):
        self.set_font("Arial", style="B", size=14)
        self.cell(0, 10, "CTG Bericht", ln=True, align='C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", size=10)
        self.set_text_color(128)
        self.cell(0, 10, f"Seite {self.page_no()}", align='C')


def generate_pdf(
    person,
    fetus_name=None,
    time_range=None,
    include_info=True,
    include_risk=True,
    include_ctg=True,
    include_image=True,
    include_ctg_plot=True,
    include_wehen=True,
    wehen_height=5.0,         # 💡 Default-Wert setzen
    wehen_distance=120,
    ctg_index=0                # 💡 Default-Wert setzen
):
    """
    Erstellt einen PDF-Bericht für eine gegebene Person mit optionalen Abschnitten:
    - Basisdaten, Risikoeinschätzung, CTG-Auswertung, Diagramm und Wehenanalyse

    Parameter:
    ----------
    person : Person
        Instanz mit Patientendaten
    fetus_name : str, optional
        Name des Fötus für die Auswertung
    time_range : tuple[int, int], optional
        Zeitbereich für das CTG-Diagramm (Start, Ende in Sekunden)
    include_info : bool
        Basisinformationen einfügen
    include_risk : bool
        Risikoeinschätzung anzeigen
    include_ctg : bool
        CTG-Statistiken einfügen
    include_image : bool
        Profilbild anzeigen
    include_ctg_plot : bool
        CTG-Diagramm erzeugen und einfügen
    include_wehen : bool
        Analyse der Wehen einfügen
    wehen_height : float
        Mindesthöhe für Wehendetektion
    wehen_distance : int
        Mindestabstand in Sekunden zwischen Wehen
    ctg_index : int
        Index der zu analysierenden CTG-Datei

    Rückgabe:
    --------
    pdf : FPDF
        Generiertes PDF-Objekt
    """
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)


    # 📌 Abschnittsüberschrift
    def section_heading(title):
        """Fügt eine farbige Abschnittsüberschrift ein."""
        pdf.set_font("Arial", size=12, style="B")
        pdf.set_fill_color(230, 230, 250)  # zartes Lila
        pdf.set_text_color(0)
        pdf.cell(0, 10, title, ln=True, fill=True)
        pdf.set_font("Arial", size=12)
        pdf.ln(2)

    # 🧍 Basisdaten
    if include_info:
        section_heading("Basisdaten")
        start_y = pdf.get_y()

        if include_image and person.picture_path and os.path.exists(person.picture_path):
            try:
                pdf.image(person.picture_path, x=140, y=start_y, w=50)
            except RuntimeError:
                pdf.set_xy(140, start_y)
                pdf.cell(50, 10, txt="⚠️ Bildfehler", ln=True)
        else:
            pdf.set_xy(140, start_y)
            pdf.cell(50, 10, txt="(Kein Bild)", ln=True)

        pdf.set_xy(10, start_y)
        pdf.set_text_color(0)
        pdf.cell(0, 10, f"Name: {person.firstname} {person.lastname}", ln=True)
        pdf.cell(0, 10, f"Alter: {person.calculate_age()} Jahre", ln=True)
        pdf.cell(0, 10, f"Geschlecht: {person.gender}", ln=True)
        pdf.cell(0, 10, f"Schwangerschaftswoche: {person.gestational_age_weeks}", ln=True)
        pdf.cell(0, 10, f"Anzahl der Föten: {person.fetuses}", ln=True)
        conditions = ", ".join(person.medical_conditions) if person.medical_conditions else "Keine"
        pdf.cell(0, 10, f"Vorerkrankungen: {conditions}", ln=True)
        pdf.ln(3)

    # ⚠️ Risikoeinschätzung
    if include_risk:
        section_heading("Risikoeinschätzung")
        risk_text = "Risikoschwangerschaft" if person.is_high_risk_pregnancy() else "Keine Risikoschwangerschaft"
        pdf.set_text_color(0)
        pdf.cell(0, 10, txt=risk_text, ln=True)
        pdf.ln(3)

    # 📊 CTG-Auswertung
    if include_ctg and person.CTG_tests:
        ctg_data = person.CTG_tests[ctg_index]
        ctg = CTG_Data(
            ctg_data["result_link"],
            fetus=next((f for f in person.fetuses_list if f.name == fetus_name), None)
        )
        ctg.read_csv()

        avg = ctg.average_HR_baby()
        max_hr = ctg.max_HR_baby()
        min_hr = ctg.min_HR_baby()

        section_heading("CTG-Auswertung")
        if fetus_name:
            pdf.cell(0, 10, f"Ausgewählter Fötus: {fetus_name}", ln=True)
            pdf.cell(0, 10, f"CTG-Datum: {ctg_data['date']}", ln=True)
        if time_range:
            pdf.cell(0, 10, f"Zeitbereich: {time_range[0]} - {time_range[1]} Sekunden", ln=True)
            pdf.cell(0, 10, f"Durchschnittliche HF: {avg:.1f} bpm", ln=True)
            pdf.cell(0, 10, f"Maximale HF: {max_hr:.1f} bpm", ln=True)
            pdf.cell(0, 10, f"Minimale HF: {min_hr:.1f} bpm", ln=True)
            pdf.ln(3)

        if include_ctg_plot:
            fig = ctg.plotly_figure(time_range=time_range, show_rangeslider=False)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpimg:
                fig.write_image(tmpimg.name, width=700, height=300, engine="kaleido")
                pdf.add_page()
                section_heading("CTG-Diagramm")
                pdf.image(tmpimg.name, x=10, w=190)

# Wehenanalyse
        if include_wehen:
            section_heading("Wehenanalyse")

            wehen = WehenAnalysis(ctg)
            df_peaks = wehen.detect_contractions(height=wehen_height, distance=wehen_distance)
            df_cat = wehen.classify_contractions(df_peaks)

            pdf.cell(0, 10, f"Minimale UC-Höhe: {wehen_height}", ln=True)
            pdf.cell(0, 10, f"Minimaler Abstand: {wehen_distance} Sekunden", ln=True)
            pdf.ln(3)

            if df_cat.empty:
                pdf.cell(0, 10, "Keine Wehen erkannt.", ln=True)
            else:
        # 📋 Tabelle 1: Detailübersicht
                pdf.set_font("Arial", style="B", size=10)
                pdf.cell(40, 8, "Zeitpunkt (min)", border=1)
                pdf.cell(50, 8, "Abstand (s)", border=1)
                pdf.cell(40, 8, "Dauer (s)", border=1)
                pdf.cell(60, 8, "Wehenart", border=1)
                pdf.ln()

                pdf.set_font("Arial", size=9)
                for _, row in df_cat.iterrows():
                    pdf.cell(40, 8, f"{row['Wehenzeitpunkt (min)']:.2f}", border=1)
                    abstand = f"{row['Abstand zur vorherigen Wehe (min)']:.1f}" if pd.notna(row['Abstand zur vorherigen Wehe (min)']) else "-"
                    pdf.cell(50, 8, abstand, border=1)
                    pdf.cell(40, 8, f"{row['Wehendauer (min)']:.1f}", border=1)
                    pdf.cell(60, 8, row['Wehenart'], border=1)
                    pdf.ln()

                pdf.ln(5)
        # 📋 Tabelle 2: Anzahl pro Kategorie
                pdf.set_font("Arial", style="B", size=10)
                pdf.cell(100, 8, "Kategorie", border=1)
                pdf.cell(40, 8, "Anzahl", border=1)
                pdf.ln()

                pdf.set_font("Arial", size=9)
                summary = df_cat['Wehenart'].value_counts().rename_axis('Kategorie').reset_index(name='Anzahl')
                for _, row in summary.iterrows():
                    pdf.cell(100, 8, str(row['Kategorie']), border=1)
                    pdf.cell(40, 8, str(row['Anzahl']), border=1)
                    pdf.ln()
    
    elif include_ctg:
        section_heading("CTG-Auswertung")
        pdf.cell(0, 10, txt="Keine CTG-Daten verfügbar.", ln=True)

    return pdf
