"""Test ponctuel de lecture/écriture avec le SDK Python InfluxDB 2."""
import os
from pathlib import Path

from dotenv import load_dotenv
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
URL = os.getenv("INFLUX_URL", "http://localhost:8086")
TOKEN = os.getenv("INFLUX_TOKEN")
ORG = os.getenv("INFLUX_ORG")
BUCKET = os.getenv("INFLUX_BUCKET")
if not all([TOKEN, ORG, BUCKET]):
    raise RuntimeError("Configuration absente : vérifier le fichier .env à la racine")

with InfluxDBClient(url=URL, token=TOKEN, org=ORG) as client:
    with client.write_api(write_options=SYNCHRONOUS) as writer:
        point = (Point("room_climate")
                 .tag("room", "salle_101")
                 .tag("sensor_id", "CAP-01")
                 .field("temperature", 23.0)
                 .field("humidity", 48.0))
        writer.write(bucket=BUCKET, org=ORG, record=point)
    print("Écriture réussie.")
    query = f'''from(bucket: "{BUCKET}")
      |> range(start: -1h)
      |> filter(fn: (r) => r._measurement == "room_climate")
      |> filter(fn: (r) => r._field == "temperature")
      |> sort(columns: ["_time"], desc: true)
      |> limit(n: 5)'''
    tables = client.query_api().query(org=ORG, query=query)
    for table in tables:
        for record in table.records:
            print(record.get_time(), record.values.get("room"), record.get_value())
