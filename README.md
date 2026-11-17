# Building Monitoring — projet NoSQL InfluxDB

Surveillance pédagogique de trois salles par capteurs virtuels de température et d'humidité.

## Phase 3 — Simulation des capteurs (InfluxDB 2)

### Préparer

InfluxDB 2 doit être démarré avec `docker compose up -d` et le bucket `building_monitoring` doit exister.
Conservez le fichier `.env` **à la racine** avec `INFLUX_TOKEN`, `INFLUX_ORG`, `INFLUX_BUCKET`. Ne publiez jamais ce fichier.

Dans PowerShell à la racine du projet :

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r python/requirements.txt
.\.venv\Scripts\python.exe python/main.py
.\.venv\Scripts\python.exe python/simulation.py
```

Stopper le simulateur avec Ctrl+C. Après 6 cycles (~50 secondes), le capteur CAP-02 enregistre une anomalie >30°C pendant 4 cycles.

Dans InfluxDB Data Explorer, sélectionner le bucket `building_monitoring` et afficher les températures sur les 15 dernières minutes, ou exécuter :

```flux
from(bucket: "building_monitoring")
  |> range(start: -15m)
  |> filter(fn: (r) => r._measurement == "room_climate")
  |> filter(fn: (r) => r._field == "temperature")
```

Le `main.py` permet un test ponctuel d'écriture et de lecture. `simulation.py` écrit trois points toutes les dix secondes.
