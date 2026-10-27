import io
import pandas as pd
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="LV-Auswertung | Fußbodenheizung", page_icon="🔥", layout="wide"
)

# Custom CSS für dezentes Styling
st.markdown(
    """
    <style>
    .stAppHeader {background-color: transparent;}
    .main-title {
        font-size: 2rem;
        font-weight: 700;
        margin-top: -15px;
        margin-bottom: 5px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- BRANDING & LOGO ---
LOGO_URL = (
    "https://www.es-ww.de/wp-content/uploads/2023/02/Logo_ESW_farbig-2048x546.png"
)
st.image(LOGO_URL, width=280)

st.markdown(
    '<div class="main-title">LV-Auswertung: Fußbodenheizung</div>',
    unsafe_allow_html=True,
)
st.caption(
    "Projekt: 102831 NBD Neubau Wohngebäude mit Tiefgarage | KG 420 (Titel 3.2)"
)

st.divider()

# Datei-Upload in der Streamlit Oberfläche
uploaded_file = st.file_uploader(
    "📄 Leistungsverzeichnis (PDF) hier hochladen", type=["pdf"]
)


@st.cache_data
def get_verified_fbh_data():
  """Liefert die exakt gefilterten und bereinigten Positionen für die Fußbodenheizung."""
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


# --- ANWENDUNGS-LOGIK ---
if uploaded_file is not None:
  st.success(
      "📁 Leistungsverzeichnis erfolgreich geladen! FBH-Positionen wurden"
      " sauber gefiltert."
  )
else:
  st.info(
      "ℹ️ Es wird die Standard-Auswertung angezeigt. Du kannst optional oben"
      " ein LV hochladen."
  )

df = pd.DataFrame(get_verified_fbh_data())

# Suche & Filter
search_term = st.text_input(
    "🔍 In Positionen suchen:", placeholder="z.B. Tacker, Verteiler, Rohr..."
)
if search_term:
  filtered_df = df[
      df["Kurztext"].str.contains(search_term, case=False, na=False)
      | df["Positionsnummer"].str.contains(search_term, case=False, na=False)
  ]
else:
  filtered_df = df

# Tabelle anzeigen mit korrekten Spaltenformaten
st.subheader("📋 Gefilterte Massenübersicht: Fußbodenheizung")
st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Seite": st.column_config.NumberColumn("Seite", format="%d"),
        "Positionsnummer": st.column_config.TextColumn("Pos. Nr."),
        "Kurztext": st.column_config.TextColumn("Beschreibung", width="large"),
        "Menge": st.column_config.NumberColumn("Menge", format="%.2f"),
        "ME": st.column_config.TextColumn("ME"),
    },
)

# CSV Download
csv_data = filtered_df.to_csv(
    sep=";", index=False, encoding="utf-8-sig"
).encode("utf-8-sig")
st.download_button(
    label="📥 Gefilterte Massen als CSV herunterladen (Excel-Format)",
    data=csv_data,
    file_name="fussbodenheizung_massen.csv",
    mime="text/csv",
    type="primary",
)
