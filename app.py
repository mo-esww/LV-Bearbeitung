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
st.caption("Flexibles Tool zur automatischen Massen-Extraktion aus PDFs")

st.divider()

# Datei-Upload in der Streamlit Oberfläche
uploaded_file = st.file_uploader(
    "📄 Leistungsverzeichnis (PDF) hier hochladen", type=["pdf"]
)


def parse_pdf_with_auto_quantities(pdf_file):
  extracted_data = []

  with pdfplumber.open(pdf_file) as pdf:
    for page_num, page in enumerate(pdf.pages, start=1):
      text = page.extract_text()
      if text:
        lines = text.split("\n")
        for line in lines:
          stripped = line.strip()

          # Sucht nach Zeilen, die mit einer Positionsnummer beginnen (z.B. 3.2.10, 4.1.20 etc.)
          match_pos = re.match(r"^(\d+[\.\d]+\d+)\s+(.*)", stripped)
          if match_pos:
            pos_nr = match_pos.group(1)
            rest_text = match_pos.group(2)

            # Versucht Menge und Einheit am Ende oder im Text zu finden (z.B. "4600 m²" oder "38000 m")
            qty_match = re.search(
                r"([\d\.,]+)\s*(m²|qm|m|Stk|stk|pausch\.?|psch)$",
                rest_text,
                re.IGNORECASE,
            )

            if qty_match:
              # Mengenformat bereinigen (Deutsche Schreibweise in Float umwandeln)
              qty_str = (
                  qty_match.group(1).replace(".", "").replace(",", ".")
              )
              try:
                menge = float(qty_str)
              except ValueError:
                menge = 0.0
              me = qty_match.group(2)
              kurztext = rest_text[: qty_match.start()].strip()
            else:
              menge = 0.0
              me = "Stk / Einheit"
              kurztext = rest_text

            extracted_data.append({
                "Seite": page_num,
                "Positionsnummer": pos_nr,
                "Kurztext": kurztext,
                "Menge": menge,
                "ME": me,
            })

  return extracted_data


# --- DYNAMISCHE STEUERUNG BEI UPLOAD ---
if uploaded_file is not None:
  with st.spinner(
      "Analysiere LV und extrahiere Positionen inklusive Massen..."
  ):
    raw_data = parse_pdf_with_auto_quantities(uploaded_file)
    if raw_data:
      df = pd.DataFrame(raw_data)
      st.success(
          f"Erfolgreich! {len(df)} Positionen mit automatischen Massen"
          " extrahiert."
      )
    else:
      df = pd.DataFrame(
          columns=["Seite", "Positionsnummer", "Kurztext", "Menge", "ME"]
      )
      st.warning(
          "Es konnten keine Positionen mit Mengen im Dokument gefunden"
          " werden."
      )
else:
  df = pd.DataFrame(
      columns=["Seite", "Positionsnummer", "Kurztext", "Menge", "ME"]
  )
  st.info(
      "ℹ️ Bitte lade oben ein Leistungsverzeichnis (PDF) hoch. Die Massen"
      " werden dann dynamisch ausgelesen."
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
st.subheader("📋 Massenübersicht")
st.dataframe(
    filtered_df,
    use_container_width=Width if "Width" in locals() else True,
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
