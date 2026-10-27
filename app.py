import csv
import io
import pandas as pd
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="LV-Auswertung | Fußbodenheizung",
    page_icon="🔥",
    layout="wide",
)


# Datenstruktur der Fußbodenheizungs-Positionen (KG 420, Titel 3.2)
def get_fbh_data():
  return [
      {
          "Seite": 82,
          "Positionsnummer": "3.2.10",
          "Kurztext": (
              "System-Clip-Platte Tacker FBH d=30-2mm (Trittschalldämmung EPS"
              " 035 DES sg)"
          ),
          "Menge": 4600.00,
          "ME": "m²",
      },
      {
          "Seite": 82,
          "Positionsnummer": "3.2.20",
          "Kurztext": (
              "Zusatzdämmung EPS 035 DEO 100 kPa / d=30mm (für FBH auf"
              " Erdreich/Kellerdecke)"
          ),
          "Menge": 500.00,
          "ME": "m²",
      },
      {
          "Seite": 82,
          "Positionsnummer": "3.2.30",
          "Kurztext": (
              "System-Heizrohr PE-Xc 5-Schicht 16 x 2,0 mm (sauerstoffdicht"
              " nach DIN 4726)"
          ),
          "Menge": 38000.00,
          "ME": "m",
      },
      {
          "Seite": 83,
          "Positionsnummer": "3.2.40",
          "Kurztext": "Randdämmstreifen mit Folienlasche, h=150mm, t=10mm",
          "Menge": 3200.00,
          "ME": "m",
      },
      {
          "Seite": 83,
          "Positionsnummer": "3.2.50",
          "Kurztext": "Fugenprofil / Dehnfugenprofil für Estriche",
          "Menge": 450.00,
          "ME": "m",
      },
      {
          "Seite": 83,
          "Positionsnummer": "3.2.60",
          "Kurztext": (
              "Schutzrohr gewellt für FBH-Rohre (Durchführung durch Fugen)"
          ),
          "Menge": 300.00,
          "ME": "m",
      },
      {
          "Seite": 83,
          "Positionsnummer": "3.2.70",
          "Kurztext": "FBH-Verteilerschrank Unterputz (UP) für 2-4 Heizkreise",
          "Menge": 12.00,
          "ME": "Stk",
      },
      {
          "Seite": 84,
          "Positionsnummer": "3.2.80",
          "Kurztext": "FBH-Verteilerschrank Unterputz (UP) für 5-8 Heizkreise",
          "Menge": 85.00,
          "ME": "Stk",
      },
      {
          "Seite": 84,
          "Positionsnummer": "3.2.90",
          "Kurztext": "FBH-Verteilerschrank Unterputz (UP) für 9-12 Heizkreise",
          "Menge": 29.00,
          "ME": "Stk",
      },
      {
          "Seite": 84,
          "Positionsnummer": "3.2.100",
          "Kurztext": (
              "Heizkreisverteiler Edelstahl für 2 Heizkreise mit"
              " Durchflussanzeigern"
          ),
          "Menge": 2.00,
          "ME": "Stk",
      },
      {
          "Seite": 84,
          "Positionsnummer": "3.2.110",
          "Kurztext": "Heizkreisverteiler Edelstahl für 3 Heizkreise",
          "Menge": 4.00,
          "ME": "Stk",
      },
      {
          "Seite": 85,
          "Positionsnummer": "3.2.120",
          "Kurztext": "Heizkreisverteiler Edelstahl für 4 Heizkreise",
          "Menge": 6.00,
          "ME": "Stk",
      },
      {
          "Seite": 85,
          "Positionsnummer": "3.2.130",
          "Kurztext": "Heizkreisverteiler Edelstahl für 5 Heizkreise",
          "Menge": 10.00,
          "ME": "Stk",
      },
      {
          "Seite": 85,
          "Positionsnummer": "3.2.140",
          "Kurztext": "Heizkreisverteiler Edelstahl für 6 Heizkreise",
          "Menge": 22.00,
          "ME": "Stk",
      },
      {
          "Seite": 85,
          "Positionsnummer": "3.2.150",
          "Kurztext": "Heizkreisverteiler Edelstahl für 7 Heizkreise",
          "Menge": 30.00,
          "ME": "Stk",
      },
      {
          "Seite": 86,
          "Positionsnummer": "3.2.160",
          "Kurztext": "Heizkreisverteiler Edelstahl für 8 Heizkreise",
          "Menge": 23.00,
          "ME": "Stk",
      },
      {
          "Seite": 86,
          "Positionsnummer": "3.2.170",
          "Kurztext": "Heizkreisverteiler Edelstahl für 9 Heizkreise",
          "Menge": 18.00,
          "ME": "Stk",
      },
      {
          "Seite": 86,
          "Positionsnummer": "3.2.180",
          "Kurztext": "Heizkreisverteiler Edelstahl für 10 Heizkreise",
          "Menge": 11.00,
          "ME": "Stk",
      },
      {
          "Seite": 86,
          "Positionsnummer": "3.2.190",
          "Kurztext": "Stellantrieb thermoelektrisch 230V stromlos geschlossen",
          "Menge": 850.00,
          "ME": "Stk",
      },
      {
          "Seite": 87,
          "Positionsnummer": "3.2.200",
          "Kurztext": "Raumthermostat Unterputz 230V mit Skala",
          "Menge": 620.00,
          "ME": "Stk",
      },
      {
          "Seite": 87,
          "Positionsnummer": "3.2.210",
          "Kurztext": (
              "Regelverteiler / Klemmleiste für FBH-Stellantriebe (8 Zonen)"
          ),
          "Menge": 126.00,
          "ME": "Stk",
      },
      {
          "Seite": 87,
          "Positionsnummer": "3.2.220",
          "Kurztext": (
              "Mess- und Funktionsheizen der FBH nach DIN EN 1264 (inkl."
              " Protokoll)"
          ),
          "Menge": 1.00,
          "ME": "pausch.",
      },
  ]


# CSV Hilfsfunktion
def convert_df_to_csv(df):
  output = io.StringIO()
  # Excel-freundliches CSV Format (Semikolon getrennt)
  df.to_csv(output, sep=";", index=False, encoding="utf-8-sig")
  return output.getvalue().encode("utf-8-sig")


# --- APP INTERFACE ---
st.title("🧱 LV-Auswertung: Fußbodenheizung (KG 420)")
st.caption(
    "Projekt: 102831 NBD Neubau Wohngebäude mit Tiefgarage (Häuser 01-03)"
)

data = get_fbh_data()
df = pd.DataFrame(data)

# KPI Kennzahlen oben anzeigen
col1, col2, col3, col4 = st.columns(4)
col1.metric("Anzahl Positionen", len(df))
col2.metric(
    "Gesamtfläche Dämmung",
    f"{df[df['ME']=='m²']['Menge'].sum():,.2f} m²".replace(",", "."),
)
col3.metric(
    "Gesamtlänge Heizrohr",
    f"{df[df['Positionsnummer']=='3.2.30']['Menge'].sum():,.0f} m".replace(
        ",", "."
    ),
)
col4.metric(
    "Verteilerschränke (Gesamt)",
    f"{int(df[df['Kurztext'].str.contains('Verteilerschrank')]['Menge'].sum())} Stk",
)

st.divider()

# Suche & Filter
search_term = st.text_input(
    "🔍 In Positionen suchen:", placeholder="z.B. Verteiler, Thermostat..."
)
if search_term:
  filtered_df = df[
      df["Kurztext"].str.contains(search_term, case=False)
      | df["Positionsnummer"].str.contains(search_term)
  ]
else:
  filtered_df = df

# Tabelle anzeigen
st.subheader("📋 Massenübersicht")
st.dataframe(
    filtered_df,
    use_container_width=True,
    column_config={
        "Seite": st.column_config.NumberColumn("Seite", format="%d"),
        "Positionsnummer": st.column_config.TextColumn("Pos. Nr."),
        "Kurztext": st.column_config.TextColumn("Beschreibung", width="large"),
        "Menge": st.column_config.NumberColumn("Menge", format="%.2f"),
        "ME": st.column_config.TextColumn("Einheit"),
    },
    hide_index=True,
)

# CSV-Download Button
csv_data = convert_df_to_csv(filtered_df)
st.download_button(
    label="📥 Massen als CSV herunterladen (für Excel)",
    data=csv_data,
    file_name="massen_fussbodenheizung.csv",
    mime="text/csv",
    type="primary",
)
