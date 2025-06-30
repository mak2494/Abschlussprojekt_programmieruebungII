import numpy as np
import pandas as pd
from scipy.signal import find_peaks, peak_widths


class WehenAnalysis:
    def __init__(self, CTG_Data):
        """
        ctg_data: Instanz von CTG_Data, bei der read_csv() schon aufgerufen wurde
        und die eine 'UC'-Spalte enthält.
        """
        self.ctg = CTG_Data
        if 'UC' not in self.ctg.df.columns:
            raise ValueError("Die UC-Spalte fehlt im DataFrame.")
        # Zeitreihen-Index in Sekunden
        self.uc = self.ctg.df['UC'].copy()
        self.uc.index = self.ctg.df.index.total_seconds()

    def detect_contractions(self, height=None, distance=None):
        """
        Findet Wehen-Peaks und bestimmt Intervalle sowie Dauer.
        Rückgabe: DataFrame mit Spalten
          - time     : Zeitpunkt (s) des Peaks
          - interval : Abstand (s) zur vorherigen Wehe (NaN bei erster)
          - duration : Dauer der Wehe (s)
        """
        y = self.uc.values
        times = self.uc.index.values

        # 1) Peaks finden
        peaks, props = find_peaks(y, height=height, distance=distance)

        # 2) Dauer als Breite auf halber Höhe
        results_half = peak_widths(y, peaks, rel_height=0.5)
        # Breite in Samples -> Sekunden
        dt = np.median(np.diff(times))
        durations = results_half[0] * dt

        # 3) Zeiten der Peaks
        peak_times = times[peaks]

        # 4) Intervalle berechnen
        intervals = np.diff(peak_times, prepend=np.nan)

        # 5) DataFrame zusammenbauen
        df = pd.DataFrame({
            'Wehenzeitpunkt (min)': peak_times/60,
            'Abstand zur vorherigen Wehe (s)': intervals,
            'Wehendauer (s)': durations,
        })
        df.reset_index(drop=True, inplace=True)  # Index entfernen
        return df

    def classify_contractions(self, df_peaks=None):
        """
        Klassifiziert jede Wehe in df_peaks nach Abstand und Dauer gemäß Tabelle.
        Rückgabe: df_peaks mit zusätzlicher Spalte 'category'.
        """
        if df_peaks is None:
            df_peaks = self.detect_contractions()

        # Kategorien: (interval_low, interval_high, dur_low, dur_high, label)
        categories = [
            (    0,   np.inf,     10,    30, "Braxton-Hicks-Wehen"),
            (    0,   np.inf,      0,    10, "Senkwehen"),
            (  600,  1200,    30,    45, "Vor-/Eröffnungswehen"),
            (  180,   300,    45,    60, "Aktive Eröffnungswehen"),
            (   60,   120,    60,    90, "Übergangswehen"),
            (  120,   180,    60,    90, "Austreibungswehen"),
        ]

        def assign_category(row):
            iv = row['Abstand zur vorherigen Wehe (s)']
            du = row['Wehendauer (s)']
            for low_i, high_i, low_d, high_d, label in categories:
                iv_ok = pd.isna(iv) or (iv >= low_i and iv < high_i)
                if iv_ok and (du >= low_d and du < high_d):
                    return label
            return "Unklassifiziert"

        df = df_peaks.copy()
        df['category'] = df.apply(assign_category, axis=1)
        return df
