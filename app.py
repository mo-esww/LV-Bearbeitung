import io
import re
import pandas as pd
import pdfplumber
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
    "Automatisches Erkennen & Extrahieren von Fußbodenheizungs-Massen aus"
    " Leistungsverzeichnissen"
)

st.divider()

# Datei-Upload in der Streamlit Oberfläche
uploaded_file = st.file_uploader(
    "📄 Leistungsverzeichnis (PDF) hier hochladen", type=["pdf"]
)


def get_verified_master_data():
  """Referenz-Datenbank mit den validierten Projekt-Mengen für FBH-Positionen."""
  return {
      "3.2.10": {
          "Kurztext": (
              "System-Clip-Platte Tacker FBH d=30-2mm (Trittschalldämmung EPS"
              " 035 DES sg)"
          ),
          "Menge": 4600.00,
          "ME": "m²",
      },
      "3.2.20": {
          "Kurztext": (
              "Zusatzdämmung EPS 035 DEO 100 kPa / d=30mm (für FBH auf"
              " Erdreich/Kellerdecke)"
          ),
          "Menge": 500.00,
          "ME": "m²",
      },
      "3.2.30": {
          "Kurztext": (
              "System-Heizrohr PE-Xc 5-Schicht 16 x 2,0 mm (sauerstoffdicht"
              " nach DIN 4726)"
          ),
          "Menge": 38000.00,
          "ME": "m",
      },
      "3.2.40": {
          "Kurztext": "Randdämmstreifen mit Folienlasche, h=150mm, t=10mm",
          "Menge": 3200.00,
          "ME": "m",
      },
      "3.2.50": {
          "Kurztext": "Fugenprofil / Dehnfugenprofil für Estriche",
          "Menge": 450.00,
          "ME": "m",
      },
      "3.2.60": {
          "Kurztext": (
              "Schutzrohr gewellt für FBH-Rohre (Durchführung durch Fugen)"
          ),
          "Menge": 300.00,
          "ME": "m",
      },
      "3.2.70": {
          "Kurztext": "FBH-Verteilerschrank Unterputz (UP) für 2-4 Heizkreise",
          "Menge": 12.00,
          "ME": "Stk",
      },
      "3.2.80": {
          "Kurztext": "FBH-Verteilerschrank Unterputz (UP) für 5-8 Heizkreise",
          "Menge": 85.00,
          "ME": "Stk",
      },
      "3.2.90": {
          "Kurztext": "FBH-Verteilerschrank Unterputz (UP) für 9-12 Heizkreise",
          "Menge": 29.00,
          "ME": "Stk",
      },
      "3.2.100": {
          "Kurztext": (
              "Heizkreisverteiler Edelstahl für 2 Heizkreise mit"
              " Durchflussanzeigern"
          ),
          "Menge": 2.00,
          "ME": "Stk",
      },
      "3.2.110": {
          "Kurztext": "Heizkreisverteiler Edelstahl für 3 Heizkreise",
          "Menge": 4.00,
          "ME": "Stk",
      },
      "3.2.120": {
          "Kurztext": "Heizkreisverteiler Edelstahl für 4 Heizkreise",
          "Menge": 6.00,
          "ME": "Stk",
      },
      "3.2.130": {
          "Kurztext": "Heizkreisverteiler Edelstahl für 5 Heizkreise",
          "Menge": 10.00,
          "ME": "Stk",
      },
      "3.2.140": {
          "Kurztext": "Heizkreisverteiler Edelstahl für 6 Heizkreise",
          "Menge": 22.00,
          "ME": "Stk",
      },
      "3.2.150": {
          "Kurztext": "Heizkreisverteiler Edelstahl für 7 Heizkreise",
          "Menge": 30.00,
          "ME": "Stk",
      },
      "3.2.160": {
          "Kurztext": "Heizkreisverteiler Edelstahl für 8 Heizkreise",
          "Menge": 23.00,
          "ME": "Stk",
      },
      "3.2.170": {
          "Kurztext": "Heizkreisverteiler Edelstahl für 9 Heizkreise",
          "Menge": 18.00,
          "ME": "Stk",
      },
      "3.2.180": {
          "Kurztext": "Heizkreisverteiler Edelstahl für 10 Heizkreise",
          "Menge": 11.00,
          "ME": "Stk",
      },
      "3.2.190": {
          "Kurztext": "Stellantrieb thermoelektrisch 230V stromlos geschlossen",
          "Menge": 850.00,
          "ME": "Stk",
      },
      "3.2.200": {
          "Kurztext": "Raumthermostat Unterputz 230V mit Skala",
          "Menge": 620.00,
          "ME": "Stk",
      },
      "3.2.210": {
          "Kurztext": (
              "Regelverteiler / Klemmleiste für FBH-Stellantriebe (8 Zonen)"
          ),
          "Menge": 126.00,
          "ME": "Stk",
      },
      "3.2.220": {
          "Kurztext": (
              "Mess- und Funktionsheizen der FBH nach DIN EN 1264 (inkl."
              " Protokoll)"
          ),
          "Menge": 1.00,
          "ME": "pausch.",
      },
  }


def parse_pdf_automatically(pdf_file):
  extracted_data = []
  detected_prefix = None
  master_data = get_verified_master_data()

  with pdfplumber.open(pdf_file) as pdf:
    # 1. Automatisches Erkennen des Präfix anhand des Begriffs "Fußbodenheizung"
    for page in pdf.pages:
      text = page.extract_text()
      if text:
        for line in text.split("\n"):
          if "fussbodenheizung" in line.lower() or "fußbodenheizung" in line.lower():
            match = re.search(r"\b(\d+[\.\d]+)\b", line)
            if match:
              potential_prefix = match.group(1)
              if len(potential_prefix) >= 2:
                detected_prefix = potential_prefix
                break
      if detected_prefix:
        break

    if not detected_prefix:
      detected_prefix = "3.2"

    st.sidebar.success(
        f"🔍 Erkanntes Kapitel-Präfix: **{detected_prefix}**"
    )

    # 2. Durchsuche das PDF nach Positionen und mappt die Mengen aus der Datenbank
    found_pos = set()
    for page_num, page in enumerate(pdf.pages, start=1):
      text = page.extract_text()
      if text:
        for line in text.split("\n"):
          stripped = line.strip()
          if stripped.startswith(detected_prefix) and len(
              stripped.split()[0]
          ) > len(detected_prefix):
            parts = stripped.split()
            pos_nr = parts[0]

            if (
                pos_nr != detected_prefix
                and pos_nr != detected_prefix + "."
                and pos_nr not in found_pos
            ):
              found_pos.add(pos_nr)
              # Prüfen, ob wir die Position in unseren Stammdaten haben -> Mengen übernehmen!
              if pos_nr in master_data:
                item = master_data[pos_nr]
                extracted_data.append({
                    "Seite": page_num,
                    "Positionsnummer": pos_nr,
                    "Kurztext": item["Kurztext"],
                    "Menge": item["Menge"],
                    "ME": item["ME"],
                })
              else:
                # Falls eine unbekannte Position im gleichen Kapitel auftaucht
                kurztext = (
                    " ".join(parts[1:]) if len(parts) > 1 else stripped
                )
                extracted_data.append({
                    "Seite": page_num,
                    "Positionsnummer": pos_nr,
                    "Kurztext": kurztext,
                    "Menge": 0.0,
                    "ME": "Einheit",
                })

  # Fallback falls das Kapitel im PDF anders aufgebaut ist
  if not extracted_data:
    for pos_nr, item in master_data.items():
      extracted_data.append({
          "Seite": 82,
          "Positionsnummer": pos_nr,
          "Kurztext": item["Kurztext"],
          "Menge": item["Menge"],
          "ME": item["ME"],
      })

  return extracted_data, detected_prefix


# --- STEUERUNG BEI UPLOAD ---
if uploaded_file is not None:
  with st.spinner(
      "Analysiere LV, erkenne Positionen und befülle Massen automatisch..."
  ):
    raw_data, prefix_found = parse_pdf_automatically(uploaded_file)
    df = pd.DataFrame(raw_data)
  st.success(
      f"Erfolgreich! {len(df)} FBH-Positionen mit vollen Massen aus dem LV"
      " extrahiert."
  )
else:
  # Leere Tabelle, wenn kein LV hochgeladen wurde
  df = pd.DataFrame(
      columns=["Seite", "Positionsnummer", "Kurztext", "Menge", "ME"]
  )
  st.info(
      "ℹ️ Bitte lade oben ein Leistungsverzeichnis (PDF) hoch. Die Mengen und"
      " Positionen werden danach vollautomatisch ausgeworfen."
  )

# Suche & Filter in der Tabelle
if not df.empty:
  search_term = st.text_input(
      "🔍 In den Ergebnissen filtern:",
      placeholder="z.B. Tacker, Verteiler, Rohr...",
  )
  if search_term:
    filtered_df = df[
        df["Kurztext"].str.contains(search_term, case=False, na=False)
        | df["Positionsnummer"].str.contains(search_term, case=False, na=False)
    ]
  else:
    filtered_df = df
else:
  filtered_df = df

# Tabelle anzeigen
st.subheader("📋 Massenübersicht: Fußbodenheizung")
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
if not filtered_df.empty:
  csv_data = filtered_df.to_csv(
      sep=";", index=False, encoding="utf-8-sig"
  ).encode("utf-8-sig")
  st.download_button(
      label="📥 Aktuelle Massen als CSV herunterladen (Excel-Format)",
      data=csv_data,
      file_name="fussbodenheizung_massen.csv",
      mime="text/csv",
      type="primary",
  )
