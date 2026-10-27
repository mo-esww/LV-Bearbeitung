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
    "Erweiterte Massen-Extraktion mit spaltenbasierter Texterkennung"
)

st.divider()

# Datei-Upload in der Streamlit Oberfläche
uploaded_file = st.file_uploader(
    "📄 Leistungsverzeichnis (PDF) hier hochladen", type=["pdf"]
)


def parse_pdf_with_coordinates(pdf_file):
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
      # Wörter mit Koordinaten auslesen, um Spalten strukturiert zuzuordnen
      words = page.extract_words()
      if not words:
        continue

      # Zeilen nach vertikaler Koordinate (top) gruppieren und horizontal (x0) sortieren
      words_sorted = sorted(words, key=lambda w: (w["top"] // 8, w["x0"]))

      lines_dict = {}
      for w in words_sorted:
        line_key = int(w["top"] // 8)
        if line_key not in lines_dict:
          lines_dict[line_key] = []
        lines_dict[line_key].append(w["text"])

      for line_key, w_list in lines_dict.items():
        line_text = " ".join(w_list)
        line_lower = line_text.lower()

        # Prüfen ob ein Keyword oder Positionsmuster enthalten ist
        if any(kw in line_lower for kw in fbh_keywords) or re.match(
            r"^\d+[\.\d]*\b", line_text.strip()
        ):
          pos_match = re.match(r"^([0-9\.]+)\b", line_text.strip())
          if pos_match:
            pos_nr = pos_match.group(1)
            if "." in pos_nr or len(pos_nr) >= 2:
              rest_text = line_text[len(pos_nr) :].strip()

              # Suche nach Menge und Einheit in der zusammengesetzten Zeile
              qty_match = re.search(
                  r"([\d\.,]+)\s*(m²|qm|m|Stk|Stück|stk|pausch\.?|psch|Pkg\.?)",
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
                kurztext = rest_text[: qty_match.start()].strip()
              else:
                menge = 0.0
                me = "Einheit"
                kurztext = rest_text

              kurztext = re.sub(r"^[\.,\-\s]+", "", kurztext).strip()

              if (
                  len(kurztext) > 3
                  and not any(
                      d["Positionsnummer"] == pos_nr
                      and d["Kurztext"] == kurztext
                      for d in extracted_data
                  )
              ):
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
  with st.spinner(
      "Analysiere Spalten und extrahiere Massen über Koordinaten..."
  ):
    raw_data = parse_pdf_with_coordinates(uploaded_file)
    if raw_data:
      df = pd.DataFrame(raw_data)
      st.success(
          f"Erfolgreich! {len(df)} Positionen inklusive Massen über"
          " Spaltenanalyse extrahiert."
      )
    else:
      df = pd.DataFrame(
          columns=["Seite", "Positionsnummer", "Kurztext", "Menge", "ME"]
      )
      st.warning(
          "Es konnten keine Massen im Dokument zugeordnet werden. Bitte prüfe"
          " das PDF."
      )
else:
  df = pd.DataFrame(
      columns=["Seite", "Positionsnummer", "Kurztext", "Menge", "ME"]
  )
  st.info(
      "ℹ️ Bitte lade oben dein Leistungsverzeichnis (PDF) hoch, um die"
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
