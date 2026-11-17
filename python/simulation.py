"""Simulation de trois capteurs de température et d'humidité pour InfluxDB 2."""
import os
import random
import time
from pathlib import Path

from dotenv import load_dotenv
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# Le fichier .env est à la racine, pas dans python/.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

URL = os.getenv("INFLUX_URL", "http://localhost:8086")
TOKEN = os.getenv("INFLUX_TOKEN")
ORG = os.getenv("INFLUX_ORG")
BUCKET = os.getenv("INFLUX_BUCKET")
if not all([TOKEN, ORG, BUCKET]):
    raise RuntimeError("INFLUX_TOKEN, INFLUX_ORG ou INFLUX_BUCKET manquant dans .env")

capteurs = [
    {"room": "salle_101", "sensor_id": "CAP-01", "temperature_base": 22.0, "humidity_base": 45.0},
    {"room": "salle_102", "sensor_id": "CAP-02", "temperature_base": 25.0, "humidity_base": 52.0},
    {"room": "salle_103", "sensor_id": "CAP-03", "temperature_base": 21.0, "humidity_base": 48.0},
]


def lancer_simulation():
    # Le mode SYNCHRONOUS confirme chaque écriture, utile pour la démo.
    with InfluxDBClient(url=URL, token=TOKEN, org=ORG) as client:
        with client.write_api(write_options=SYNCHRONOUS) as writer:
            cycle = 0
            print("Simulation lancée : 3 capteurs, envoi toutes les 10 secondes. CTRL+C pour arrêter.")
            while True:
                cycle += 1
                points = []
                for capteur in capteurs:
                    temperature = capteur["temperature_base"] + random.uniform(-0.5, 0.5)
                    humidity = capteur["humidity_base"] + random.uniform(-2, 2)
                    # Exemple d'anomalie explicable à l'oral, limitée à la salle 102.
                    if capteur["sensor_id"] == "CAP-02" and 6 <= cycle <= 9:
                        temperature += 8
                    temperature = round(temperature, 2)
                    humidity = round(humidity, 2)
                    point = (Point("room_climate")
                             .tag("room", capteur["room"])
                             .tag("sensor_id", capteur["sensor_id"])
                             .field("temperature", temperature)
                             .field("humidity", humidity))
                    points.append(point)
                    print(f"{capteur['room']} | {capteur['sensor_id']} | {temperature} °C | {humidity} %")
                writer.write(bucket=BUCKET, org=ORG, record=points)
                print(f"Cycle {cycle} écrit avec succès. Prochain envoi dans 10 s.\n")
                time.sleep(10)


if __name__ == "__main__":
    try:
        lancer_simulation()
    except KeyboardInterrupt:
        print("\nSimulation arrêtée.")
