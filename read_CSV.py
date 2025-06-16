import pandas as pd
import numpy as np
import plotly.io as pio
import plotly.graph_objects as go
pio.renderers.default = "browser"  # Plotly in Browser anzeigen

## zuvor pdm plotly
## ggf. auch pdm nbformat
import plotly.express as px


def read_my_csv(filepath):
    # Einlesen eines DataFrames mit der Spalte 'timestamp' als Index
    df = pd.read_csv(filepath, index_col='time', parse_dates=True)

    # Gibt den geladenen DataFrame zurück
    return df

def plot_data(df):
    # Erstellen eines Liniendiagramms mit Plotly Express
    fig = px.line(df, x=df.index, y=df.columns, title='CTG Data Over Time')

    # Anzeigen des Diagramms
    fig.show()

if __name__ == "__main__":
    df = read_my_csv("data/CTG_data/CTG_data2.csv")
    plot_data(df)