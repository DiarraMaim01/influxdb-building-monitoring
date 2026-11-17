import os
import time
import random
from pathlib import Path

from dotenv import load_dotenv
from influxdb_client_3 import InfluxDBClient3

# 1. Charger le fichier .env
DOSSIER = Path(__file__).resolve().parent
load_dotenv(DOSSIER / ".env")

# 2. Récupérer le token
TOKEN = os.getenv("INFLUXDB3_AUTH_TOKEN")

HOST = "http://localhost:8181"
DATABASE = "batiment"

if not TOKEN:
    raise ValueError("Token absent : vérifiez le fichier .env")

# 3. Définir nos trois capteurs virtuels
capteurs = [
    {
        "room": "salle_101",
        "sensor_id": "CAP-01",
        "temperature_base": 22.0,
        "humidity_base": 45.0
    },
    {
        "room": "salle_102",
        "sensor_id": "CAP-02",
        "temperature_base": 25.0,
        "humidity_base": 52.0
    },
    {
        "room": "salle_103",
        "sensor_id": "CAP-03",
        "temperature_base": 21.0,
        "humidity_base": 48.0
    }
]

# 4. Connexion à InfluxDB
client = InfluxDBClient3(
    host=HOST,
    token=TOKEN,
    database=DATABASE
)

try:
    print("Simulation des capteurs démarrée !")
    print("Envoi des mesures toutes les 10 secondes.")
    print("Appuyez sur CTRL+C pour arrêter.\n")

    while True:

        # Parcourir les trois capteurs
        for capteur in capteurs:

            # Générer des valeurs légèrement variables
            temperature = round(
                capteur["temperature_base"] + random.uniform(-0.5, 0.5), 2
            )

            humidity = round(
                capteur["humidity_base"] + random.uniform(-2, 2), 2
            )

            # Construire la mesure au format Line Protocol
            mesure = (
                f"room_climate,"
                f"room={capteur['room']},"
                f"sensor_id={capteur['sensor_id']} "
                f"temperature={temperature},"
                f"humidity={humidity}"
            )

            # Envoyer la mesure dans InfluxDB
            client.write(record=mesure)

            print(
                f"{capteur['room']} | "
                f"{capteur['sensor_id']} | "
                f"Température : {temperature} °C | "
                f"Humidité : {humidity} %"
            )

        print("\nProchain envoi dans 10 secondes...\n")

        time.sleep(10)

except KeyboardInterrupt:
    print("\nArrêt de la simulation demandé.")

except Exception as erreur:
    print("Erreur pendant la simulation :", erreur)

finally:
    client.close()
    print("Connexion InfluxDB fermée.")