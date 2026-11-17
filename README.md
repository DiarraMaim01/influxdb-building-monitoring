# Building Monitoring — projet NoSQL InfluxDB

Surveillance pédagogique de trois salles par capteurs virtuels de température et d'humidité.

## Phase 5 — Analyses temporelles avec Python et InfluxDB 2

### Objectif
Interroger les mesures `room_climate` déjà écrites par `simulation.py`, sans toucher aux scripts existants. Calculer la température moyenne, la température maximale et repérer les dépassements de 30 °C.

### Prérequis
- InfluxDB 2 démarré (`docker compose ps`).
- `.env` à la racine avec les valeurs `INFLUX_TOKEN`, `INFLUX_ORG`, `INFLUX_BUCKET`.
- Dépendances de `python/requirements.txt` déjà installées.
- Des mesures `room_climate` de moins de 7 jours dans le bucket.

### Exécuter
À la racine du dépôt, dans PowerShell :

```powershell
.\.venv\Scripts\python.exe python/analyse.py
```

Si aucune donnée n'apparaît, exécuter `python/simulation.py` pendant 10 cycles, l'arrêter avec `Ctrl+C`, puis relancer `analyse.py`.

### Modèle et requêtes
- Measurement : `room_climate`
- Tags : `room`, `sensor_id`
- Field : `temperature`
- Temps : 7 derniers jours
- Agrégations Flux : `group()` + `mean()` et `max()`
- Détection des anomalies : `filter(_value > 30.0)`

**Attention** : une mesure isolée créée par `main.py` peut entrer dans les moyennes. Les données historiques et les simulations successives peuvent aussi modifier les résultats. Les valeurs sont donc à vérifier sur les données effectivement stockées.

## Critères de validation
1. Le script affiche trois salles pour les moyennes et les maximums (si les trois capteurs ont écrit récemment).
2. Les événements de température >30 °C apparaissent quand le simulateur a exécuté les cycles 6 à 9.
3. Les mêmes requêtes peuvent être copiées dans le Script Editor de Data Explorer (en remplaçant `BUCKET` par le nom réel).
