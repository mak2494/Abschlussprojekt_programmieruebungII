def clean_csv():
    df = pd.read_csv("data/CTG_data/CTG_data2.csv")
    
    # Nur bestimmte Spalten behalten
    df = df[['LB', 'UC']]

    # Time spalte zufügen
    df['time'] = np.arange(0, 0.5 * len(df), 0.5)

    # Neue Datei speichern
    df.to_csv("data/CTG_data/CTG_data2.csv", index=False)

# Verwendung
clean_csv()