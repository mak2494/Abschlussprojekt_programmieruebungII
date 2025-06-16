import pandas as pd
import numpy as np
import plotly.io as pio
import plotly.graph_objects as go
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
    
        self.df = pd.read_csv(self.filepath, index_col='time', parse_dates=True)
        return self.df

    def plotly_figure(self, title="CTG Data Over Time"):
        if self.df is None:
            raise ValueError("CSV wurde noch nicht eingelesen. Bitte zuerst read_csv() aufrufen.")

        fig = go.Figure()

        # Alle Spalten, die mit "LB" anfangen, finden
        lb_columns = [col for col in self.df.columns if col.startswith('LB')]

        # Jede LB-Spalte als eigene Linie plotten
        for lb_col in lb_columns:
            fig.add_trace(go.Scatter(x=self.df.index, y=self.df[lb_col], mode='lines', name=lb_col))

        fig.add_trace(go.Scatter(x=self.df.index, y=self.df['UC'], mode='lines', name='UC'))

        fig.update_layout(title=title, xaxis_title='Zeit', yaxis_title='Wert')

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