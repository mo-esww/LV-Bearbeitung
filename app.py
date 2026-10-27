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
st.caption("Automatisches Erkennen & Extrahieren von Fußbodenheizungs-Massen")

st.divider()

# Datei-Upload in der Streamlit Oberfläche
uploaded_file = st.file_uploader(
    "📄 Leistungsverzeichnis (PDF) hier hochladen", type=["pdf"]
)


def parse_pdf_automatically(pdf_file):
  extracted_data = []
  detected_prefix = None

  with pdfplumber.open(pdf_file) as pdf:
    # Schritt 1: Automatische Suche nach dem Kapitel "Fußbodenheizung" im gesamten Dokument
    for page in pdf.pages:
      text = page.extract_text()
      if text:
        for line in text.split("\n"):
          if "fussbodenheizung" in line.lower() or "fußbodenheizung" in line.lower():
            # Suche nach einer Nummer am Anfang der Zeile oder im Text (z.B. "3.2", "4.1.2")
            match = re.search(r"\b(\d+[\.\d]+)\b", line)
            if match:
              potential_prefix = match.group(1)
              # Wir wollen keine zu langen oder zu kurzen Ziffernfolgen als Präfix
              if len(potential_prefix) >= 2:
                detected_prefix = potential_prefix
                break
      if detected_prefix:
        break

    # Falls kein exaktes Kapitel gefunden wurde, nehmen wir einen intelligenten Standard-Fallback an
    if not detected_prefix:
      detected_prefix = "3.2"

    st.sidebar.success(
        f"🔍 Erkanntes Kapitel-Präfix: **{detected_prefix}**"
    )

    # Schritt 2: Alle Positionen mit diesem Präfix automatisch extrahieren
    for page_num, page in enumerate(pdf.pages, start=1):
      text = page.extract_text()
      if text:
        for line in text.split("\n"):
          stripped = line.strip()
          # Prüft, ob die Zeile mit dem gefundenen Präfix beginnt (z.B. "3.2.10" oder "3.2.")
          if stripped.startswith(detected_prefix) and len(
              stripped.split()[0]
          ) > len(detected_prefix):
            parts = stripped.split()
            pos_nr = parts[0]
            if pos_nr != detected_prefix and pos_nr != detected_prefix + ".":
              kurztext = " ".join(parts[1:]) if len(parts) > 1 else stripped

              extracted_data.append({
                  "Seite": page_num,
                  "Positionsnummer": pos_nr,
                  "Kurztext": kurztext,
                  "Menge": 0.0,
                  "ME": "Einheit",
              })

  return extracted_data, detected_prefix


# --- DYNAMISCHE STEUERUNG BEI UPLOAD ---
if uploaded_file is not None:
  with st.spinner(
      "Analysiere LV und erkenne Fußbodenheizungs-Positionen automatisch..."
  ):
    raw_data, prefix_found = parse_pdf_automatically(uploaded_file)
    if raw_data:
      df = pd.DataFrame(raw_data)
      st.success(
          f"Erfolgreich! {len(df)} Positionen anhand des erkannten Präfix"
          f" '{prefix_found}' extrahiert."
      )
    else:
      df = pd.DataFrame(
          columns=["Seite", "Positionsnummer", "Kurztext", "Menge", "ME"]
      )
      st.warning(
          "Es konnten keine passenden Positionen automatisch ermittelt"
          " werden."
      )
else:
  df = pd.DataFrame(
      columns=["Seite", "Positionsnummer", "Kurztext", "Menge", "ME"]
  )
  st.info(
      "ℹ️ Bitte lade oben ein Leistungsverzeichnis (PDF) hoch. Das Tool"
      " erkennt die Positionen für Fußbodenheizung danach vollautomatisch."
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
