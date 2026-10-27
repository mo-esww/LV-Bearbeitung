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
    "Intelligente Massen-Extraktion mit automatischer Mengenerkennung aus PDFs"
)

st.divider()

# Datei-Upload in der Streamlit Oberfläche
uploaded_file = st.file_uploader(
    "📄 Leistungsverzeichnis (PDF) hier hochladen", type=["pdf"]
)


def parse_pdf_with_smart_quantities(pdf_file):
  extracted_data = []
  fbh_keywords = [
      "tacker",
      "heizrohr",
      "pe-xc",
      "randdämmstreifen",
      "fugenprofil",
      "schutzrohr",
      "verteilerschrank",
      "heizkreisverteiler",
      "stellantrieb",
      "raumthermostat",
      "regelverteiler",
      "klemmleiste",
      "dämmung",
      "clip-platte",
      "fussbodenheizung",
      "fußbodenheizung",
  ]

  with pdfplumber.open(pdf_file) as pdf:
    for page_num, page in enumerate(pdf.pages, start=1):
      text = page.extract_text()
      if text:
        lines = text.split("\n")
        for line in lines:
          line_lower = line.lower()

          if any(keyword in line_lower for keyword in fbh_keywords):
            stripped = line.strip()

            # Positionsnummer am Anfang suchen
            pos_match = re.match(r"^([0-9\.]+)\s+(.*)", stripped)
            if pos_match:
              pos_nr = pos_match.group(1)
              rest_text = pos_match.group(2)
            else:
              pos_nr = "3.2.X"
              rest_text = stripped

            # FLEXIBLE MENGEN-ERKENNUNG:
            # Sucht im Text nach einer Zahl (mit Tausenderpunkten/Dezimal komma) gefolgt von einer Einheit
            qty_match = re.search(
                r"(\d{1,3}(?:\.\d{3})*(?:,\d+)?|\d+(?:,\d+)?)\s*(m²|qm|m|Stk|Stück|stk|pausch\.?|psch|Pkg\.?)",
                rest_text,
                re.IGNORECASE,
            )

            if qty_match:
              qty_str = (
                  qty_match.group(1).replace(".", "").replace(",", ".")
              )
              try:
                menge = float(qty_str)
              except ValueError:
                menge = 0.0
              me = qty_match.group(2)
              # Text vor der gefundenen Menge als Beschreibung nutzen
              kurztext = rest_text[: qty_match.start()].strip()
            else:
              menge = 0.0
              me = "Einheit"
              kurztext = rest_text

            # Bereinigung des Kurztexts (unnötige Bindestriche oder überflüssige Reste entfernen)
            kurztext = re.sub(r"[\.,\-]+$", "", kurztext).strip()

            if not any(
                d["Kurztext"] == kurztext for d in extracted_data
            ) and len(kurztext) > 4:
              extracted_data.append({
                  "Seite": page_num,
                  "Positionsnummer": pos_nr,
                  "Kurztext": kurztext,
                  "Menge": menge,
                  "ME": me,
              })

  return extracted_data


# --- STEUERUNG BEI UPLOAD ---
if uploaded_file is not None:
  with st.spinner("Analysiere LV und extrahiere Positionen inklusive Massen..."):
    raw_data = parse_pdf_with_smart_quantities(uploaded_file)
    if raw_data:
      df = pd.DataFrame(raw_data)
      st.success(
          f"Erfolgreich! {len(df)} Positionen mit erkannten Massen extrahiert."
      )
    else:
      df = pd.DataFrame(
          columns=["Seite", "Positionsnummer", "Kurztext", "Menge", "ME"]
      )
      st.warning("Es konnten keine passenden Positionen ermittelt werden.")
else:
  df = pd.DataFrame(
      columns=["Seite", "Positionsnummer", "Kurztext", "Menge", "ME"]
  )
  st.info(
      "ℹ️ Bitte lade oben ein Leistungsverzeichnis (PDF) hoch, um die"
      " Auswertung zu starten."
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
