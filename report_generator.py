import os
import tempfile
from fpdf import FPDF
from read_CSV import CTG_Data
from plotly.colors import qualitative

class PDF(FPDF):
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
    include_info=True,
    include_risk=True,
    include_ctg=True,
    include_image=True,
    include_ctg_plot=True
):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # 📌 Abschnittsüberschrift
    def section_heading(title):
        pdf.set_font("Arial", size=12, style="B")
        pdf.set_fill_color(230, 230, 250)  # zartes Lila
        pdf.set_text_color(0)
        pdf.cell(0, 10, title, ln=True, fill=True)
        pdf.set_font("Arial", size=12)
        pdf.ln(2)

    # 🧍 Basisdaten
    if include_info:
        section_heading("Basisdaten")

        if include_image and person.picture_path and os.path.exists(person.picture_path):
            try:
                pdf.image(person.picture_path, x=70, y=pdf.get_y(), w=70)
                pdf.ln(60)
            except RuntimeError:
                pdf.cell(200, 10, txt="⚠️ Bild konnte nicht geladen werden.", ln=True)
        else:
            pdf.cell(200, 10, txt="(Kein Bild verfügbar)", ln=True)

        pdf.set_text_color(0)
        pdf.cell(0, 10, f"Name: {person.firstname} {person.lastname}", ln=True)
        pdf.cell(0, 10, f"Alter: {person.calculate_age()} Jahre", ln=True)
        pdf.cell(0, 10, f"Geschlecht: {person.gender}", ln=True)
        pdf.cell(0, 10, f"Schwangerschaftswoche: {person.gestational_age_weeks}", ln=True)
        pdf.cell(0, 10, f"Anzahl der Föten: {person.fetuses}", ln=True)
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
        ctg = CTG_Data(
            person.CTG_tests[0]["result_link"],
            fetus=person.fetuses_list[0] if person.fetuses_list else None
        )
        ctg.read_csv()

        avg = ctg.average_HR_baby()
        max_hr = ctg.max_HR_baby()
        min_hr = ctg.min_HR_baby()

        section_heading("CTG-Auswertung")
        pdf.set_text_color(0)
        pdf.cell(0, 10, f"Durchschnittliche HF: {avg:.1f} bpm", ln=True)
        pdf.cell(0, 10, f"Maximale HF: {max_hr:.1f} bpm", ln=True)
        pdf.cell(0, 10, f"Minimale HF: {min_hr:.1f} bpm", ln=True)
        pdf.ln(3)

        # 📈 Diagramm einfügen
        if include_ctg_plot:
            fig = ctg.plotly_figure()  # 🔁 Kein title mehr erlaubt

            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpimg:
                fig.write_image(tmpimg.name, width=700, height=300)
                pdf.add_page()
                section_heading("CTG-Diagramm")
                pdf.ln(5)
                pdf.image(tmpimg.name, x=10, w=190)

    elif include_ctg:
        section_heading("CTG-Auswertung")
        pdf.set_text_color(0)
        pdf.cell(0, 10, txt="Keine CTG-Daten verfügbar.", ln=True)

    return pdf