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


    def plotly_figure(self, title="CTG Data Over Time"):
        if self.df is None:
            raise ValueError("CSV wurde noch nicht eingelesen. Bitte zuerst read_csv() aufrufen.")

        # 1) Downsampling nur ab >2000 Punkten
        n = len(self.df)
        if n > 2000:
            factor = int(n / 2000)  # so ergibt sich ca. 2000 Punkte
            df_plot = self.df.iloc[::factor]
        else:
            df_plot = self.df

        # 2) Index in Sekunden
        x = df_plot.index.total_seconds()

        fig = go.Figure()

        # 3) Fetale Herzfrequenz per WebGL
        for lb in [c for c in df_plot.columns if c.startswith("LB")]:
            fig.add_trace(go.Scattergl(
                x=x,
                y=df_plot[lb],
                mode='lines',
                name=lb,
                line=dict(width=2),
                yaxis='y1'
            ))

        # 4) UC als gefüllte WebGL-Linie
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

         # 5) X-Ticks alle 10 Sekunden
        maxs = int(x.max())
        ticks = list(range(0, maxs + 1, 10))  # 0, 10, 20, …, maxs

        fig.update_layout(
            title=title,
            template='simple_white',
            hovermode='x unified',   # gemeinsames Hoverfenster
            dragmode='zoom',         # Zoom & Pan aktiv
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
                range=[0, 300],  # Anfangsbereich: 5 Minuten
                rangeslider=dict(visible=True),  # Scrollbalken aktivieren
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
                range=[-5, df_plot['UC'].max() * 1.1 if 'UC' in df_plot.columns else 1],
                dtick=(df_plot['UC'].max() / 5) if 'UC' in df_plot.columns else 1
            )
        )

        return fig


    
    def get_lb_column(self):
        if self.fetus is None:
            for col in ['LB', 'LB1', 'LB2']:
                if col in self.df.columns:
                    return col
            raise ValueError("Keine LB-Spalte im DataFrame gefunden.")

        try:
            fetus_index = int(self.fetus.name.split()[-1])
        except Exception:
            fetus_index = 1

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