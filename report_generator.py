"""
generate_report.py

Dieses Modul erstellt PDF-Berichte zu CTG-Messungen und Personendaten.
Es unterstützt optionale Inhalte wie Basisdaten, Risikoeinschätzung,
Herzfrequenzanalysen, CTG-Diagramme und Wehenanalysen.
"""
from fpdf import FPDF
from read_CSV import CTG_Data
from wehen_analysis import WehenAnalysis
import pandas as pd
import os
import tempfile
import matplotlib.pyplot as plt
import io

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


def plot_ctg_with_matplotlib(df, lb_col, start_s, end_s, width=700, height=300):
    """
    Zeichnet CTG-Verlauf aus DataFrame. Nutzt gezielt die Spalte lb_col für FHR und optional 'UC'.
    """
    # Zeit in Sekunden als eigene Spalte
    plot_df = df.copy().reset_index()
    plot_df['time'] = plot_df['time'].dt.total_seconds()

    fig, ax = plt.subplots(figsize=(width/100, height/100))
    # FHR-Daten: nur die gewählte Spalte
    ax.plot(plot_df['time'], plot_df[lb_col], label=lb_col)
    ax.set_xlim(start_s, end_s)
    ax.set_xlabel("Zeit (s)")
    ax.set_ylabel("Herzfrequenz (bpm)")
    ax.legend(loc='upper right')
    # UC (Wehen)
    if 'UC' in plot_df.columns:
        ax2 = ax.twinx()
        ax2.plot(plot_df['time'], plot_df['UC'], color='gray', alpha=0.5, label='UC')
        ax2.set_ylabel("UC")
        ax2.set_ylim(plot_df['UC'].min(), plot_df['UC'].max())
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    return buf


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
    wehen_height=5.0,
    wehen_distance=120,
    ctg_index=0
):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    def section_heading(title):
        pdf.set_font("Arial", size=12, style="B")
        pdf.set_fill_color(230, 230, 250)
        pdf.set_text_color(0)
        pdf.cell(0, 10, title, ln=True, fill=True)
        pdf.set_font("Arial", size=12)
        pdf.ln(2)

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
        pdf.cell(0, 10, f"Name: {person.firstname} {person.lastname}", ln=True)
        pdf.cell(0, 10, f"Alter: {person.calculate_age()} Jahre", ln=True)
        pdf.cell(0, 10, f"Geschlecht: {person.gender}", ln=True)
        pdf.cell(0, 10, f"Schwangerschaftswoche: {person.gestational_age_weeks}", ln=True)
        pdf.cell(0, 10, f"Anzahl der Föten: {person.fetuses}", ln=True)
        conditions = ", ".join(person.medical_conditions) if person.medical_conditions else "Keine"
        pdf.cell(0, 10, f"Vorerkrankungen: {conditions}", ln=True)
        pdf.ln(3)

    if include_risk:
        section_heading("Risikoeinschätzung")
        risk_text = "Risikoschwangerschaft" if person.is_high_risk_pregnancy() else "Keine Risikoschwangerschaft"
        pdf.cell(0, 10, txt=risk_text, ln=True)
        pdf.ln(3)

    if include_ctg and person.CTG_tests:
        ctg_data = person.CTG_tests[ctg_index]
        ctg = CTG_Data(
            ctg_data["result_link"],
            fetus=next((f for f in person.fetuses_list if f.name == fetus_name), None)
        )
        df_ctg = ctg.read_csv()

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
            start_s, end_s = time_range or (0, 0)
            # Bestimme die LB-Spalte für den ausgewählten Fötus
            lb_col = ctg.get_lb_column()
            img_buf = plot_ctg_with_matplotlib(df_ctg, lb_col, start_s, end_s)
            # Temporäre Datei für das PNG erstellen
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmpfile:
                tmpfile.write(img_buf.getvalue())
                tmpfile.flush()
                pdf.add_page()
                section_heading("CTG-Diagramm")
                pdf.image(tmpfile.name, x=10, w=190)

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
