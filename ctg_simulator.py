import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import time
import plotly.graph_objects as go
import numpy as np
import io
import wave
import base64

class CTGSimulator:
    def __init__(self, csv_path: str, lb_col: str, bpm_threshold: float = 110.0, interval: float = 1.0):
        """
        csv_path: Pfad zur CTG-Datei (CSV)
        lb_col: Spalte mit fetaler Herzfrequenz
        bpm_threshold: Schwellwert für den Alarm (bpm)
        interval: Sekunden pro Simulationsschritt
        """
        self.csv_path = csv_path
        self.lb_col = lb_col
        self.bpm_threshold = bpm_threshold
        self.interval = interval
        self.df = None

        # Session-State initialisieren
        if 'sim_alerts' not in st.session_state:
            st.session_state['sim_alerts'] = []
        if 'sim_running' not in st.session_state:
            st.session_state['sim_running'] = False

    def load(self):
        """Lädt die CSV und wandelt den Index in Timedelta um."""
        self.df = pd.read_csv(self.csv_path, index_col='time')
        self.df.index = pd.to_timedelta(self.df.index, unit='s')
        if self.lb_col not in self.df.columns:
            raise ValueError(f"Spalte '{self.lb_col}' nicht gefunden in {self.csv_path}")

    def _generate_beep(self, freq=440, duration_ms=200, volume=0.5, sample_rate=44100) -> bytes:
        """Erzeugt einen einfachen Sinus-Beep als WAV-Byte-Stream."""
        t = np.linspace(0, duration_ms/1000, int(sample_rate * duration_ms/1000), False)
        tone = (volume * np.sin(2 * np.pi * freq * t)).astype(np.float32)

        buf = io.BytesIO()
        with wave.open(buf, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16 bit
            wf.setframerate(sample_rate)
            wf.writeframes((tone * 32767).astype(np.int16).tobytes())
        buf.seek(0)
        return buf.read()

    def run_live(self):
        """
        Führt die Live-Simulation aus, spielt Alarm-Töne automatisch ab und
        zeigt alle Alarm-Messages auch nach Stoppen der Simulation.
        """
        if self.df is None:
            self.load()

        # Markiere Simulation als aktiv
        st.session_state['sim_running'] = True

        metric_pl = st.empty()
        chart_pl  = st.empty()

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[], y=[], mode="lines", name="FHR"))
        fig.update_layout(
            xaxis_title="Zeit (s)",
            yaxis_title="Herzfrequenz (bpm)",
            template="simple_white"
        )

        x_data = []
        y_data = []

        for tdelta, row in self.df.iterrows():
            if not st.session_state['sim_running']:
                break

            bpm = row[self.lb_col]
            metric_pl.metric("Fetale Herzfrequenz (bpm)", f"{bpm:.1f}")

            # Daten anhängen und Chart aktualisieren
            x_data.append(tdelta.total_seconds())
            y_data.append(bpm)
            fig.data[0].x, fig.data[0].y = x_data, y_data
            chart_pl.plotly_chart(fig, use_container_width=True)
            st.session_state['sim_last_fig'] = fig

            # Alarm prüfen
            if bpm < self.bpm_threshold:
                msg = f"⚠️ Alarm! FHR unter {self.bpm_threshold} bpm: aktuell {bpm:.1f} bpm"
                st.error(msg)
                st.session_state['sim_alerts'].append(msg)

                # Beep automatisch abspielen
                beep = self._generate_beep()
                b64 = base64.b64encode(beep).decode('utf-8')
                components.html(
                    f"""
                    <audio autoplay>
                      <source src="data:audio/wav;base64,{b64}" type="audio/wav">
                    </audio>
                    """, height=0
                )

            time.sleep(self.interval)

        # Ende der Simulation
        st.session_state['sim_running'] = False
        st.success("✅ Simulation gestoppt.")

        # Alle gesammelten Alarm-Messages anzeigen
        if st.session_state['sim_alerts']:
            st.warning("🔔 Alarm-Übersicht während der Simulation:")
            for alert in st.session_state['sim_alerts']:
                st.error(alert)

    def run(self):
        """Starte die Live-Simulation und bereite Alerts vor."""
        # Nur beim Start neu leeren
        st.session_state['sim_alerts'] = []
        self.run_live()
