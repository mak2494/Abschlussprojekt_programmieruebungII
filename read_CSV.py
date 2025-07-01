import pandas as pd
import numpy as np
import plotly.io as pio
import plotly.graph_objects as go
from plotly.colors import qualitative
pio.renderers.default = "browser"  # Plotly in Browser anzeigen

## zuvor pdm plotly
## ggf. auch pdm nbformat
import plotly.express as px


class CTG_Data:
    def __init__(self, filepath, fetus=None):
        self.filepath = filepath
        self.df = None
        self.fetus = fetus  # Verknüpfter Fötus (optional)
    def read_csv(self):
        # Liest die CSV-Datei ein und verwendet die Spalte 'time' als Index.
    
        self.df = pd.read_csv(
            self.filepath, 
            index_col='time', 
            parse_dates=False)
        self.df.index = pd.to_timedelta(self.df.index, unit='s')  # Konvertiert Zeit in Timedelta
        return self.df


    def plotly_figure(self, time_range=None):
        if self.df is None:
            raise ValueError("CSV wurde noch nicht eingelesen. Bitte zuerst read_csv() aufrufen.")

    # Optional Zeitbereich beschränken (z. B. fürs PDF)
        df_plot = self.df.copy()
        if time_range:
            start_sec, end_sec = time_range
            df_plot = df_plot[(df_plot.index.total_seconds() >= start_sec) &
                              (df_plot.index.total_seconds() <= end_sec)]

    # X-Achse (Zeit in Sekunden)
        x = df_plot.index.total_seconds()

        fig = go.Figure()

    # Nur die relevante LB-Spalte für den Fötus zeichnen
        try:
            lb_col = self.get_lb_column()
        except ValueError as e:
            lb_col = None  # Falls kein LB gefunden wurde

        if lb_col and lb_col in df_plot.columns:
            fig.add_trace(go.Scattergl(
                x=x,
                y=df_plot[lb_col],
                mode='lines',
                name=lb_col,
                line=dict(width=2, color="blue"),
                yaxis='y1'
            ))

    # UC-Kurve ebenfalls zeichnen
        if 'UC' in df_plot.columns:
            fig.add_trace(go.Scattergl(
                x=x,
                y=df_plot['UC'],
                mode='lines',
                name='UC',
                line=dict(width=1, dash='dot'),
                fill='tozeroy',
                fillcolor='rgba(0,200,0,0.2)',
                yaxis='y2'
            ))

    # X-Achsen-Ticks berechnen
        maxs = int(x.max()) if len(x) > 0 else 300
        ticks = list(range(0, maxs + 1, 10))

        fig.update_layout(
            template='simple_white',
            hovermode='x unified',
            dragmode='zoom',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            margin=dict(l=60, r=60, t=50, b=40),
            xaxis=dict(
                title='Zeit (s)',
                tickmode='array',
                tickvals=ticks,
                ticktext=[str(t) for t in ticks],
                showgrid=True,
                gridcolor='lightgrey',
                ticks='outside',
                range=[ticks[0], ticks[-1]] if ticks else None,
                rangeslider=dict(visible=True),
                type='linear'
            ),
            yaxis=dict(
                title='Fetal Heart Rate (BPM)',
                showgrid=True,
                gridcolor='lightgrey',
                range=[70, 200],
                dtick=10
            ),
            yaxis2=dict(
                title='Uterine Contractions (mmHg)',
                overlaying='y',
                side='right',
                showgrid=False,
                range=[-5, df_plot['UC'].max() * 1.1 if 'UC' in df_plot.columns else 50],
                dtick=(df_plot['UC'].max() / 5) if 'UC' in df_plot.columns else 10
            )
        )

        return fig


    
    def get_lb_column(self):
        if self.fetus is None:
        # Kein Fötus angegeben – versuche LB, LB1, LB2 der Reihe nach
            for col in ['LB', 'LB1', 'LB2']:
                if col in self.df.columns:
                    return col
            raise ValueError("Keine LB-Spalte im DataFrame gefunden.")

    # 🧠 Fötusname auswerten (z.B. "Fötus 2")
        try:
            if isinstance(self.fetus, str) and "Fötus" in self.fetus:
                fetus_index = int(self.fetus.strip().split()[-1])  # → 1 oder 2
            else:
                fetus_index = int(self.fetus.name.strip().split()[-1])
        except Exception:
            fetus_index = 1

    # 🧬 Entsprechende Spalte wählen
        possible_cols = [f'LB{fetus_index}', 'LB']
        for col in possible_cols:
            if col in self.df.columns:
                return col

        raise ValueError(f"Keine passende LB-Spalte für Fötus {fetus_index} gefunden.")


    def average_HR_baby(self):
        lb_col = self.get_lb_column()
        return self.df[lb_col].mean()

    def max_HR_baby(self):
        lb_col = self.get_lb_column()
        return self.df[lb_col].max()

    def min_HR_baby(self):
        lb_col = self.get_lb_column()
        return self.df[lb_col].min()
    
    
# Beispiel-Verwendung
if __name__ == "__main__":
    ctg = CTG_Data("data/CTG_data/CTG_twins_healthy.csv")
    ctg.read_csv()
    ctg.plotly_figure().show()
    print(f"Durchschnittliche Herzfrequenz des Babys: {ctg.average_HR_baby()} BPM")
    print(f"Maximale Herzfrequenz des Babys: {ctg.max_HR_baby()} BPM")