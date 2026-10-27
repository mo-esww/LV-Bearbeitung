import io
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
    "Projekt: 102831 NBD Neubau Wohngebäude mit Tiefgarage | KG 420 (Titel 3.2)"
)

st.divider()

# Datei-Upload in der Streamlit Oberfläche
uploaded_file = st.file_uploader(
    "📄 Leistungsverzeichnis (PDF) hier hochladen", type=["pdf"]
)


def parse_pdf_dynamic(pdf_file):
  extracted_data = []
  with pdfplumber.open(pdf_file) as pdf:
    for page_num, page in enumerate(pdf.pages, start=1):
      text = page.extract_text()
      if text:
        lines = text.split("\n")
        for line in lines:
          # Suche nach Zeilen, die mit "3.2." beginnen
          stripped = line.strip()
          if stripped.startswith("3.2.") and len(stripped.split()[0]) > 4:
            parts = stripped.split()
            pos_nr = parts[0]
            kurztext = " ".join(parts[1:]) if len(parts) > 1 else stripped

            extracted_data.append({
                "Seite": page_num,
                "Positionsnummer": pos_nr,
                "Kurztext": kurztext,
                "Menge": 0.0,
                "ME": "Einheit",
            })
  return extracted_data


# --- DYNAMISCHE STEUERUNG BEI UPLOAD ---
if uploaded_file is not None:
  with st.spinner("Analysiere hochgeladenes Leistungsverzeichnis..."):
    raw_data = parse_pdf_dynamic(uploaded_file)
    if raw_data:
      df = pd.DataFrame(raw_data)
      st.success(
          f"Erfolgreich! {len(df)} Positionen aus dem neuen LV extrahiert und"
          " aktualisiert."
      )
    else:
      df = pd.DataFrame(
          columns=["Seite", "Positionsnummer", "Kurztext", "Menge", "ME"]
      )
      st.warning(
          "Es wurden keine passenden Positionen mit dem Start '3.2.' im"
          " Dokument gefunden."
      )
else:
  # Wenn keine Datei hochgeladen ist oder sie gelöscht wurde -> Leere Tabelle
  df = pd.DataFrame(
      columns=["Seite", "Positionsnummer", "Kurztext", "Menge", "ME"]
  )
  st.info(
      "ℹ️ Bitte lade oben ein Leistungsverzeichnis (PDF) hoch, um die Tabelle"
      " zu füllen."
  )

# Suche & Filter (nur aktiv wenn Daten vorhanden)
if not df.empty:
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

# CSV Download (nur anzeigen, wenn Daten da sind)
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
