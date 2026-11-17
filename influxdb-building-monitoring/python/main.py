import os
from pathlib import Path

import pandas as pd
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

# 3. Créer le client InfluxDB
client = InfluxDBClient3(
    host=HOST,
    token=TOKEN,
    database=DATABASE
)

try:
    print("Connexion à InfluxDB réussie !")

    # 4. WRITE : envoyer une nouvelle mesure
    mesure = (
        "room_climate,room=salle_101,sensor_id=CAP-01 "
        "temperature=23.0,humidity=48.0"
    )

    client.write(record=mesure)

    print("Nouvelle mesure enregistrée avec succès !")

    # 5. READ : lire les 5 dernières mesures
    resultat = client.query(
        query="SELECT * FROM room_climate ORDER BY time DESC LIMIT 5"
    )

    print("\nDernières mesures enregistrées :")

    df = resultat.to_pandas()
    print(df.to_string(index=False))

except Exception as erreur:
    print("Erreur :", erreur)

finally:
    client.close()
    print("\nConnexion fermée.")