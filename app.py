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
st.caption("Flexibles Tool zur automatischen Massen-Extraktion aus PDFs")

st.divider()

# --- SEITENLEISTE FÜR FLEXIBLE EINSTELLUNGEN ---
with st.sidebar:
  st.header("⚙️ Such-Einstellungen")
  st.markdown(
      "Hier kannst du anpassen, nach welchem Positions-Präfix gesucht werden"
      " soll, falls das Gewerk in einem anderen LV eine andere Nummer hat."
  )

  # Flexibles Eingabefeld für das Präfix (Standard ist "3.2.")
  target_prefix = st.text_input(
      "Positions-Präfix (z.B. 3.2., 4.1.)",
      value="3.2.",
      help="Das Tool sucht nach allen Positionen, die mit diesem Kürzel beginnen.",
  )

# Datei-Upload in der Streamlit Oberfläche
uploaded_file = st.file_uploader(
    "📄 Leistungsverzeichnis (PDF) hier hochladen", type=["pdf"]
)


def parse_pdf_dynamic(pdf_file, prefix):
  extracted_data = []
  with pdfplumber.open(pdf_file) as pdf:
    for page_num, page in enumerate(pdf.pages, start=1):
      text = page.extract_text()
      if text:
        lines = text.split("\n")
        for line in lines:
          stripped = line.strip()
          # Dynamische Suche basierend auf dem vom Nutzer eingegebenen Präfix
          if stripped.startswith(prefix) and len(stripped.split()[0]) > len(
              prefix
          ):
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
  with st.spinner(f"Analysiere LV nach Positionen mit '{target_prefix}'..."):
    raw_data = parse_pdf_dynamic(uploaded_file, target_prefix)
    if raw_data:
      df = pd.DataFrame(raw_data)
      st.success(
          f"Erfolgreich! {len(df)} Positionen mit Präfix '{target_prefix}'"
          " extrahiert."
      )
    else:
      df = pd.DataFrame(
          columns=["Seite", "Positionsnummer", "Kurztext", "Menge", "ME"]
      )
      st.warning(
          f"Keine Positionen mit dem Präfix '{target_prefix}' im Dokument"
          " gefunden. Prüfe das Präfix in der Seitenleiste!"
      )
else:
  # Leere Tabelle, wenn kein LV hochgeladen wurde
  df = pd.DataFrame(
      columns=["Seite", "Positionsnummer", "Kurztext", "Menge", "ME"]
  )
  st.info(
      "ℹ️ Bitte lade oben ein Leistungsverzeichnis (PDF) hoch. Passe bei Bedarf"
      " links in der Seitenleiste das Such-Präfix an."
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

# CSV Download (nur wenn Daten vorhanden sind)
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
