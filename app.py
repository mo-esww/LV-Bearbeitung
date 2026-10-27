import csv
import sys


def export_fbh_massen_to_csv(output_csv_path="fussbodenheizung_massen.csv"):
  """Filtert die Positionen für die Fußbodenheizung (Titel 3.2)

  aus dem Leistungsverzeichnis und exportiert sie als CSV-Datei.
  """

  # Strukturierte Daten der Fußbodenheizungs-Positionen (KG 420, Titel 3.2)
  fbh_daten = [
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

  # Schreiben der Daten in eine CSV-Datei
  try:
    with open(
        output_csv_path, mode="w", newline="", encoding="utf-8-sig"
    ) as csv_file:
      fieldnames = ["Seite", "Positionsnummer", "Kurztext", "Menge", "ME"]
      writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter=";")

      writer.writeheader()
      for row in fbh_daten:
        writer.writerow(row)

    print(
        f"[INFO] CSV-Export erfolgreich! Datei gespeichert unter:"
        f" '{output_csv_path}'"
    )

  except Exception as e:
    print(f"[FEHLER] Beim Schreiben der CSV-Datei ist ein Fehler aufgetreten: {e}")
    sys.exit(1)


if __name__ == "__main__":
  print("Starte Extraktion der Fußbodenheizungs-Massen...")
  export_fbh_massen_to_csv()
