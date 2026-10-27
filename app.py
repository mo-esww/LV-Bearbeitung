import streamlit as st
import pandas as pd
import pypdf
import re
import io

# --- Seiten-Konfiguration & Corporate Design ---
st.set_page_config(
    page_title="Fußbodenheizung Positionen-Analysator", 
    page_icon="♨️",
    layout="wide"
)

# Eigene CSS-Anpassungen mit dem Farbcode #4bb6c4 (Identisch zum Bivalenz-Rechner)
st.markdown("""
    <style>
    .main {
        background-color: #f9f9f9;
    }
    h1 {
        color: #111111;
    }
    h2, h3 {
        color: #4bb6c4 !important;
    }
    .stButton>button {
        background-color: #4bb6c4;
        color: white;
        border-radius: 5px;
        width: 100%;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #3aa2af;
        color: white;
    }
    [data-testid="stMetricValue"] {
        color: #4bb6c4;
    }
    </style>
""", unsafe_allow_html=True)

# --- Kopfbereich mit Logo und Titel ---
col_logo, col_title = st.columns([1, 3])
with col_logo:
    st.image("https://www.es-ww.de/wp-content/uploads/2023/02/Logo_ESW_farbig-2048x546.png", width=280)

with col_title:
    st.title("Fußbodenheizung Positionen-Analysator")
    st.markdown("*Automatische Analyse von LV-PDFs und Angeboten auf relevante Gewerk-Positionen*")
    st.markdown("*Extrahiert Positionen, Mengen, Einheiten und Beträge mit Bezug zu Flächenheizung & Zubehör*")

st.markdown("---")

# --- Such-Keywords für Fußbodenheizung ---
DEFAULT_KEYWORDS = [
    "fußbodenheizung", "fussbodenheizung", "flächenheizung", "flaechenheizung",
    "heizkreis", "heizkreisverteiler", "stellantrieb", "tackerplatte", "noppenplatte",
    "systemrohr", "heizrohr", "trittschalldämmung", "randdämmstreifen", "verteilerschrank",
    "raumthermostat", "regelklemmleiste", "estrichzusatz", "spülarmatur", "durchflussmesser"
]

# --- Hilfsfunktionen für Text-Parsing ---
def extract_text_from_pdf(pdf_file):
    reader = pypdf.PdfReader(pdf_file)
    extracted_data = []
    
    for page_num, page in enumerate(reader.pages, start=1):
        text = page.extract_text()
        if text:
            extracted_data.append((page_num, text))
            
    return extracted_data

def parse_pdf_positions(pages_data, keywords):
    pattern = re.compile(r'|'.join(re.escape(kw) for kw in keywords), re.IGNORECASE)
    
    found_positions = []

    for page_num, text in pages_data:
        # Aufteilung in Absätze / Positionen
        lines = text.split('\n')
        
        current_block = []
        for line in lines:
            line_str = line.strip()
            if not line_str:
                if current_block:
                    block_text = " ".join(current_block)
                    if pattern.search(block_text):
                        found_positions.append({
                            "Seite": page_num,
                            "Text": block_text
                        })
                    current_block = []
            else:
                current_block.append(line_str)
                
        # Letzten Block der Seite prüfen
        if current_block:
            block_text = " ".join(current_block)
            if pattern.search(block_text):
                found_positions.append({
                    "Seite": page_num,
                    "Text": block_text
                })

    return found_positions

def parse_details_from_text(text):
    """Sucht nach typischen Mustern wie Pos-Nr, Menge, Einheit und Preisen."""
    pos_nr_match = re.search(r'\b(\d+\.\d+(\.\d+)?)\b', text)
    menge_match = re.search(r'(\d+([.,]\d+)?)\s*(m²|qm|m|Stck|Stück|Set|m2)', text, re.IGNORECASE)
    preis_match = re.search(r'(\d+([.,]\d+)?)\s*€', text)
    
    pos_nr = pos_nr_match.group(1) if pos_nr_match else "N/A"
    menge = menge_match.group(0) if menge_match else "N/A"
    preis = preis_match.group(0) if preis_match else "N/A"
    
    return pos_nr, menge, preis

# --- 1. Eingabemöglichkeit & Upload ---
st.subheader("1. Datei-Upload & Suchkriterien")

col_input1, col_input2 = st.columns(2)

with col_input1:
    uploaded_file = st.file_uploader("PDF-Leistungsverzeichnis oder Angebot hochladen", type=["pdf"])
    
with col_input2:
    st.markdown("### Erweiterte Filtereinstellungen")
    user_keywords_input = st.text_area(
        "Suchbegriffe (kommagetrennt)",
        value=", ".join(DEFAULT_KEYWORDS),
        height=100
    )
    keywords_list = [k.strip() for k in user_keywords_input.split(",") if k.strip()]

st.markdown("---")

# --- Hauptlogik & Auswertung ---
if uploaded_file is not None:
    st.subheader("📊 Auswertung der relevanten Positionen")
    
    with st.spinner("PDF wird analysiert..."):
        pages_data = extract_text_from_pdf(uploaded_file)
        matches = parse_pdf_positions(pages_data, keywords_list)

    if matches:
        # Daten-Aufbereitung
        results = []
        for idx, match in enumerate(matches, 1):
            pos_nr, menge, preis = parse_details_from_text(match["Text"])
            results.append({
                "Pos. Nr.": pos_nr,
                "Seite": match["Seite"],
                "Extrahierter Text / Beschreibung": match["Text"],
                "Menge / Einheit": menge,
                "Preis": preis
            })
            
        df_res = pd.DataFrame(results)

        # Res-Metrics anzeigen
        res_col1, res_col2, res_col3 = st.columns(3)
        with res_col1:
            st.metric(label="Gefundene Positionen", value=f"{len(df_res)} Stk.")
        with res_col2:
            st.metric(label="Durchsuchte Seiten", value=f"{len(pages_data)} Seiten")
        with res_col3:
            st.metric(label="Aktive Suchbegriffe", value=f"{len(keywords_list)} Begr.")

        st.markdown("### 📋 Detaillierte Positionsübersicht")
        
        # Interaktive Datentabelle
        st.dataframe(
            df_res,
            use_container_width=True,
            column_config={
                "Extrahierter Text / Beschreibung": st.column_config.TextColumn(width="large"),
            }
        )

        # Excel/CSV Export
        st.markdown("### 📥 Ergebnisse exportieren")
        col_exp1, col_exp2 = st.columns(2)
        
        csv_data = df_res.to_csv(index=False).encode('utf-8')
        with col_exp1:
            st.download_button(
                label="📄 Als CSV herunterladen",
                data=csv_data,
                file_name="fußbodenheizung_positionen.csv",
                mime="text/csv"
            )

    else:
        st.warning("⚠️ Es wurden keine Positionen gefunden, die zu den Suchbegriffen passen.")
else:
    st.info("💡 Bitte lade oben eine PDF-Datei hoch, um die automatische Erkennung zu starten.")
