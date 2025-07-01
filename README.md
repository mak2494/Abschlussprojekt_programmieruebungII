
# 🩺 CTG APP – Analyse & Verwaltung von Schwangerschaftsdaten

Dies ist eine interaktive **Streamlit-Webanwendung**, mit der Schwangerschaftsdaten erfasst, visualisiert und ausgewertet werden können. Ein besonderes Augenmerk liegt dabei auf **CTG-Daten** (Kardiotokografie), die zur Überwachung der fetalen Herzfrequenz verwendet werden.

---

## 🚀 Funktionen

### 👤 Versuchspersonen anzeigen
- Auswahl existierender Personen
- Anzeige von Profilbild, Alter, Geschlecht, Vorerkrankungen, Anzahl Föten und Schwangerschaftswoche
- Bearbeitungsformular zur Aktualisierung der Daten
- Erkennung von **Risikopatientinnen** (z. B. Mehrlingsschwangerschaft, Bluthochdruck, Alter > 35)

### 📊 CTG-Auswertung
- Anzeige von Herzfrequenzstatistiken (Durchschnitt, Minimum, Maximum)
- Liniendiagramm der Herzfrequenz über Zeit
- Unterscheidung von mehreren Föten durch farbige Linien
- Optional: UC-Kurve (Wehenaktivität)
- Wehenanalyse mit Kategorisierung (leicht / mittel / stark)

### ➕ Neue Personen anlegen
- Erfassung neuer Patientendaten inkl. Profilbild, Vorerkrankungen und Geburtsdatum (ab 1950)
- Upload von CTG-Daten (mehrere CSV-Dateien möglich)
- Automatische Speicherung der Daten in einer JSON-Datenbank

### 📄 PDF-Bericht generieren
- Auswahl der Inhalte (Basisdaten, Risikoeinschätzung, CTG-Daten, Wehenanalyse etc.)
- Eingrenzung des CTG-Zeitraums möglich
- Download als PDF-Datei mit eingebettetem Bild und Diagramm

### ▶️ Live-Simulation
- CTG-Daten in Echtzeit mit konfigurierbarem Alarm (Herzfrequenzgrenze)
- Auswahl eines Fötus und Simulationstempo

---

## 🗂️ Projektstruktur
```
Abschlussprojekt_programmieruebungII/
│
├── main.py # Haupt-Skript mit Streamlit-Interface
├── Person.py # Personen- & Fötus-Klassen
├── read_CSV.py # CTG-Daten-Klasse mit Visualisierung & Statistik
├── report_generator.py # PDF-Erzeugung mit fpdf
├── wehen_analysis.py # Logik zur Wehenanalyse
├── ctg_simulator.py # Live-Simulation der CTG-Werte
│
├── data/
│ ├── person_db.json # JSON-Datenbank mit Versuchspersonen
│ ├── pictures/ # Profilbilder als PNG
│ └── CTG_data/ # Hochgeladene CTG-CSV-Dateien
│
└── ...
```

---

## 💾 Beispiel-CSV

Ein gültiges Beispiel enthält z. B.:

```csv
time,LB,UC
2025-01-01 08:00:00,140,20
2025-01-01 08:00:05,138,19
...

---

## 🛠️ Installation

1. **Projekt klonen**
   ```bash
   git clone <REPO_URL>
   cd Abschlussprojekt_programmieruebungII
   ```

2. **Abhängigkeiten mit [pdm](https://pdm.fming.dev/latest/) installieren**
   ```bash
   pdm install
   ```

3. **Starten der App**
   ```bash
   pdm run streamlit run main.py
   ```

---

## 📦 Abhängigkeiten (Auszug)

- `streamlit`
- `fpdf`
- `pandas` 
- `numpy`
- `plotly`
- `kaleido`
- `scipy`
- `nbformat`

---

## 📌 Hinweise

- Die Anwendung speichert alle Daten **lokal** im Verzeichnis `data/`.
- Die App ist **nicht für den klinischen Einsatz geeignet**, sondern dient ausschließlich zu **Lern- und Analysezwecken**.
- Es wird empfohlen, die Anwendung im **Chrome-Browser** zu nutzen, da nur dieser vollständig unterstützt wird.
- Die JSON-Datei `data/person_db.json` wird beim Anlegen oder Bearbeiten **dauerhaft verändert**.
- CTG-Dateien müssen das Format mit den Spaltennamen `time`, `LB`, `UC` einhalten.  
  Weitere Spalten wie `LB1`, `LB2` für Mehrlingsschwangerschaften werden ebenfalls unterstützt.

---

## 📸 Vorschau

*Screenshot kann hier eingefügt werden*

---

## 👩‍💻 Entwickelt im Rahmen des Moduls „Programmierübungen 2“

- 💼 Management Center Innsbruck
- 👩‍🔬 Studierende: Marie Köhl und Hannah Kleutgens
- 📅 Sommersemester 2025 MGST