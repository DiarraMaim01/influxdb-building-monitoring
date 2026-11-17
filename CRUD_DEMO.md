# Démonstration CRUD — InfluxDB 2

Projet : **Building Monitoring** — Cours NoSQL

## Objectif

Montrer les quatre opérations CRUD sur une mesure isolée (`crud_demo`) et comparer les résultats entre **CLI** (PowerShell + Docker) et **interface graphique** (Data Explorer). Les données du simulateur dans `room_climate` ne sont pas modifiées.

> Les commandes ont été validées pendant la préparation du projet sur InfluxDB 2. Le scénario utilise un timestamp fixe afin de pouvoir être rejoué. Il faut réinsérer le point au début de chaque répétition après l'avoir supprimé.

## 0. Prérequis

- Docker Desktop démarré ; exécuter `docker compose up -d` depuis la racine du dépôt.
- Conteneur : `building-monitoring-influxdb2`.
- Organisation : `eseo` ; bucket : `building_monitoring`.
- Fichier `.env` **local** à la racine contenant `INFLUX_TOKEN` (ne jamais publier ce fichier).
- Interface web : <http://localhost:8086>.

Dans **PowerShell** à la racine du projet :

```powershell
docker compose ps
docker exec building-monitoring-influxdb2 influx ping

# Charger le token du fichier local sans l'afficher dans le terminal.
$line = Get-Content .env | Where-Object { $_ -match '^INFLUX_TOKEN=' } | Select-Object -First 1
if (-not $line) { throw 'INFLUX_TOKEN absent du fichier .env' }
$env:INFLUX_TOKEN = $line.Substring('INFLUX_TOKEN='.Length).Trim()
if (-not $env:INFLUX_TOKEN) { throw 'INFLUX_TOKEN est vide' }
```

**Ne pas exécuter** `docker compose down -v` pour réinitialiser la démonstration : cela pourrait supprimer des volumes de données.

## 1. CREATE — insérer un point

```powershell
docker exec -e "INFLUX_TOKEN=$env:INFLUX_TOKEN" building-monitoring-influxdb2 influx write --bucket building_monitoring --org eseo --precision s "crud_demo,room=salle_101,sensor_id=TEST-01 temperature=35.5,humidity=60.0 1794916800"
```

- Measurement : `crud_demo`
- Tags : `room=salle_101`, `sensor_id=TEST-01`
- Fields : `temperature=35.5`, `humidity=60.0`
- Timestamp fixe : `1794916800` secondes Unix, soit **17 novembre 2026, 12:00 UTC (13:00 à Paris)**.

La CLI peut ne rien afficher en cas de succès : **vérifier avec une lecture**.

## 2. READ — interroger les valeurs

Dans **InfluxDB → Data Explorer → Script Editor**, coller :

```flux
from(bucket: "building_monitoring")
  |> range(start: 2026-11-17T00:00:00Z, stop: 2026-11-19T00:00:00Z)
  |> filter(fn: (r) => r._measurement == "crud_demo")
  |> filter(fn: (r) => r.sensor_id == "TEST-01")
  |> yield(name: "result")
```

Cliquer **Submit**, puis activer **View Raw Data** pour lire les lignes `_field` / `_value`.

**Résultat attendu après CREATE :** `temperature = 35.5` et `humidity = 60.0`.

La même lecture via **CLI** :

```powershell
docker exec -e "INFLUX_TOKEN=$env:INFLUX_TOKEN" building-monitoring-influxdb2 influx query 'from(bucket: "building_monitoring") |> range(start: 2026-11-17T00:00:00Z, stop: 2026-11-19T00:00:00Z) |> filter(fn: (r) => r._measurement == "crud_demo" and r.sensor_id == "TEST-01")'
```

Le sélecteur « Past 15m » de l'interface ne doit pas vous induire en erreur : **la requête ci-dessus a des bornes temporelles explicites**. Éviter ici `aggregateWindow()` pour observer la valeur exacte, sans calcul de moyenne.

## 3. UPDATE — corriger la température

La valeur 35.5 °C est erronée : la bonne valeur est 24.0 °C. InfluxDB 2 n'utilise pas un `UPDATE` SQL classique pour cela : **réécrire un point** avec la même measurement, les mêmes tags et le même timestamp remplace la valeur du field commun et préserve les fields non réécrits.

```powershell
docker exec -e "INFLUX_TOKEN=$env:INFLUX_TOKEN" building-monitoring-influxdb2 influx write --bucket building_monitoring --org eseo --precision s "crud_demo,room=salle_101,sensor_id=TEST-01 temperature=24.0 1794916800"
```

Relancer la requête du §2 :

- `temperature = 24.0`
- `humidity = 60.0` (inchangée)

**Explication à l'oral :** l'identité d'un point dépend de sa measurement, de son jeu de tags et de son timestamp. C'est une réécriture ciblée et non une mise à jour SQL arbitraire.

## 4. DELETE — supprimer uniquement le point de test

```powershell
docker exec -e "INFLUX_TOKEN=$env:INFLUX_TOKEN" building-monitoring-influxdb2 influx delete --bucket building_monitoring --org eseo --start 2026-11-17T11:59:59Z --stop 2026-11-17T12:00:01Z --predicate '_measurement="crud_demo" AND sensor_id="TEST-01"'
```

Relancer la requête du §2 : **No Results**.

⚠️ **Ne jamais omettre le prédicat par inadvertance :** sans `--predicate`, les données du bucket comprises dans la fenêtre temporelle seraient concernées, même celles d'autres measurements. Ne pas élargir la fenêtre temporelle sans raison.

## 5. Rejouer la démonstration

- Après **DELETE**, réexécuter **CREATE**, puis READ, UPDATE et DELETE dans cet ordre.
- Si la démo a été interrompue après UPDATE : refaire CREATE avec `35.5` ; puis vérifier via READ avant de poursuivre.
- Si le point existe déjà, la commande CREATE avec les mêmes tags et timestamp réécrit ses fields ; elle ne crée pas une nouvelle ligne temporelle distincte.
- Pour vérifier que le simulateur n'a pas été touché, interroger la measurement `room_climate` séparément.

## 6. Déroulé oral (4–5 minutes)

| Temps indicatif | Interaction | À dire |
|---|---|---|
| 0:00–1:00 | CLI : CREATE ; UI : READ | Le point est horodaté, ses tags identifient le capteur et ses fields sont les valeurs |
| 1:00–2:00 | CLI : READ | La même donnée est lisible par requête Flux en CLI |
| 2:00–3:15 | CLI : UPDATE ; UI : READ | Réécriture du même point, humidité conservée |
| 3:15–4:30 | CLI : DELETE ; UI : READ | Suppression ciblée, `No Results` |

**Plan B :** une capture ou une vidéo de la démo complète, conservée localement, ne remplace pas la démo live sauf incident.

## 7. Références officielles

- [Influx CLI — write](https://docs.influxdata.com/influxdb/v2/reference/cli/influx/write/)
- [Influx CLI — delete](https://docs.influxdata.com/influxdb/v2/reference/cli/influx/delete/)
- [Suppression des données InfluxDB 2](https://docs.influxdata.com/influxdb/v2/write-data/delete-data/)
