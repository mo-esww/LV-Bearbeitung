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
# Einbinden deines Firmenlogos per Direkt-URL
LOGO_URL = (
    "https://www.es-ww.de/wp-content/uploads/2023/02/Logo_ESW_farbig-2048x546.png"
)
st.image(LOGO_URL, width=280)

# Hauptüberschrift & Beschreibung
st.markdown(
    '<div class="main-title">LV-Auswertung: Fußbodenheizung</div>',
    unsafe_allow_html=True,
)
st.caption(
    "Automatischer FBH-Filter & Massen-Extraktion für Leistungsverzeichnisse"
)

st.divider()

# Datei-Upload in der Streamlit Oberfläche
uploaded_file = st.file_uploader(
    "📄 Leistungsverzeichnis (PDF) hier hochladen", type=["pdf"]
)


def get_default_fbh_data():
  """Liefert die gefilterten Positionen für die Fußbodenheizung (Titel 3.2)."""
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
              "Zusatzdämmung EPS 035 DEO 100 kPa
