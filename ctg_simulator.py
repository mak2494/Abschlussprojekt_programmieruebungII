# ctg_simulator.py

import streamlit as st
import pandas as pd
import time
import plotly.graph_objects as go

class CTGSimulator:
    def __init__(self, csv_path: str, lb_col: str, bpm_threshold: float = 110.0, interval: float = 1.0):
        """
        csv_path: Pfad zur CTG-CSV
        lb_col: Spalte mit fetaler Herzfrequenz (z.B. 'LB1' oder 'LB')
        bpm_threshold: Schwellwert für Alarm
        interval: Sekunden pro Schritt (kann angepasst werden)
        """
        self.csv_path = csv_path
        self.lb_col = lb_col
        self.bpm_threshold = bpm_threshold
        self.interval = interval
        self.df = None

    def load(self):
        """Liest die CSV und wandelt den Index in Timedelta um."""
        self.df = pd.read_csv(self.csv_path, index_col='time')
        self.df.index = pd.to_timedelta(self.df.index, unit='s')
        if self.lb_col not in self.df.columns:
            raise ValueError(f"Spalte '{self.lb_col}' nicht gefunden in {self.csv_path}")

    def run_live(self):
        """
        Zeigt die fetale Herzfrequenz als sich füllenden Plotly-Chart in einem Durchlauf
        und feuert Alarm-Logs, wenn der Schwellenwert unterschritten wird.
        """
        # Daten sicher laden
        if self.df is None:
            self.load()

        # Platzhalter für Metric und Chart
        metric_pl = st.empty()
        chart_pl = st.empty()

        # Initial-Figur anlegen
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[],
            y=[],
            mode="lines",
            name="FHR"
        ))
        fig.update_layout(
            xaxis_title="Zeit (s)",
            yaxis_title="Herzfrequenz (bpm)",
            template="simple_white"
        )

        # Schleife über alle Datenpunkte
        for time_delta, row in self.df.iterrows():
            bpm = row[self.lb_col]

            # Metric aktualisieren
            metric_pl.metric("Fetale Herzfrequenz (bpm)", f"{bpm:.1f}")

            # Aktuelle Listen extrahieren, erweitern und neu zuweisen
            x_vals = list(fig.data[0].x) + [time_delta.total_seconds()]
            y_vals = list(fig.data[0].y) + [bpm]
            fig.data[0].x = x_vals
            fig.data[0].y = y_vals

            # Figure neu rendern
            chart_pl.plotly_chart(fig, use_container_width=True)

            # Alarm
            if bpm < self.bpm_threshold:
                st.error(f"⚠️ Alarm! FHR unter {self.bpm_threshold} bpm (aktuell {bpm:.1f})")

            time.sleep(self.interval)

        st.success("✅ Simulation beendet (Ende der Daten).")

    def run(self):
        """Alias für bestehende Aufrufe: startet die Live-Simulation."""
        self.run_live()
