
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

### ➕ Neue Personen anlegen
- Erfassung neuer Patientendaten inkl. Bild, Vorerkrankungen und Geburtsdatum
- Upload von CTG-Daten (CSV-Dateien)
- Automatische Speicherung der Daten in einer JSON-Datenbank

### 📄 PDF-Bericht generieren
- Wahlweise mit Basisdaten, Risikoeinschätzung, CTG-Auswertung, Bild & Diagramm
- Automatischer PDF-Export zum Download

---

## 🗂️ Projektstruktur

```
Abschlussprojekt_programmieruebungII/
│
├── main.py                     # Haupt-Skript mit Streamlit-Interface
├── Person.py                  # Personen- & Fötus-Klassen
├── read_CSV.py                # CTG-Daten-Klasse mit Visualisierung & Statistik
├── report_generator.py        # PDF-Erzeugung mit fpdf
├── data/
│   ├── person_db.json         # Datenbank mit Versuchspersonen
│   ├── pictures/              # Bilder der Versuchspersonen
│   └── CTG_data/              # CTG-CSV-Dateien
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
```

- `LB`: Herzfrequenz eines Fötus (oder `LB1`, `LB2` bei mehreren)
- `UC`: Wehenaktivität (optional)

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
- `pandas`, `numpy`
- `plotly`
- `kaleido` (für Diagramm-Export in PDF)

---

## 📌 Hinweise

- Die App speichert neue Personen persistent in `data/person_db.json`.
- Wenn keine CTG-Datei oder kein Bild hochgeladen wird, wird dies automatisch behandelt.
- Für vollständige Funktionalität sollte die CSV-Datei die erwarteten Spalten enthalten (`LB`, `UC`).

---

## 📸 Vorschau

*Screenshot kann hier eingefügt werden*

---

## 👩‍💻 Entwickelt im Rahmen des Moduls „Programmierübungen 2“

- 💼 Hochschule XY
- 👩‍🔬 Studierende: *Dein Name hier*
- 📅 Sommersemester 2025