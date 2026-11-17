"""Analyses temporelles du bâtiment à l'aide d'InfluxDB 2 / Flux."""
import os
from pathlib import Path

from dotenv import load_dotenv
from influxdb_client import InfluxDBClient

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
URL = os.getenv("INFLUX_URL", "http://localhost:8086")
TOKEN = os.getenv("INFLUX_TOKEN")
ORG = os.getenv("INFLUX_ORG")
BUCKET = os.getenv("INFLUX_BUCKET")

if not all((TOKEN, ORG, BUCKET)):
    raise RuntimeError("Variables INFLUX_TOKEN, INFLUX_ORG ou INFLUX_BUCKET manquantes dans .env")

# Relancer simulation.py si les mesures datent de plus de sept jours.
BASE = f'''from(bucket: "{BUCKET}")
  |> range(start: -7d)
  |> filter(fn: (r) => r._measurement == "room_climate")
  |> filter(fn: (r) => r._field == "temperature")'''

REQUETES = {
    "Température moyenne par salle": BASE + '''
  |> group(columns: ["room", "sensor_id"])
  |> mean(column: "_value")''',
    "Température maximale par salle": BASE + '''
  |> group(columns: ["room", "sensor_id"])
  |> max(column: "_value")''',
    "Dépassements de 30 °C": BASE + '''
  |> filter(fn: (r) => r._value > 30.0)
  |> sort(columns: ["_time"])''',
}


def afficher_resultats(titre, tables):
    print(f"\n=== {titre} ===")
    compteur = 0
    for table in tables:
        for record in table.records:
            compteur += 1
            salle = record.values.get("room", "?")
            capteur = record.values.get("sensor_id", "?")
            valeur = record.get_value()
            heure = record.values.get("_time")
            moment = f" | {heure.isoformat()}" if titre == "Dépassements de 30 °C" and heure else ""
            print(f"{salle} / {capteur} : {valeur:.2f} °C{moment}")
    if compteur == 0:
        print("Aucune mesure trouvée sur les 7 derniers jours.")


with InfluxDBClient(url=URL, token=TOKEN, org=ORG) as client:
    for titre, flux in REQUETES.items():
        tables = client.query_api().query(org=ORG, query=flux)
        afficher_resultats(titre, tables)
