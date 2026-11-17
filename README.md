# Building Monitoring — projet NoSQL InfluxDB

Surveillance pédagogique de trois salles par capteurs virtuels de température et d'humidité.

## Phase 2 — installation InfluxDB 2

**Prérequis** : Docker Desktop, Docker Compose.

1. Copier `.env.example` vers `.env` **à la racine** et remplacer `INFLUX_PASSWORD` et `INFLUX_TOKEN` par des valeurs longues et uniques.
2. Depuis le répertoire du projet :
   ```powershell
   docker compose config
   docker compose up -d
   docker compose ps
   ```
3. Ouvrir `http://localhost:8086` et se connecter avec l'utilisateur et le mot de passe de `.env`.
4. Dans Load Data > Buckets, vérifier `building_monitoring` ; vérifier l'organisation `eseo` dans les réglages.
5. Vérifier la version (commande alternative) :
   ```powershell
   docker exec building-monitoring-influxdb2 influxd version
   ```

### Précautions

- La première initialisation (organisation/bucket/token) n'est faite **qu'avec des volumes vides**. Modifier `.env` après le premier démarrage ne recrée pas les identifiants.
- Ne pas exécuter `docker compose down -v` sur une instance contenant des données à conserver : cela détruit ses volumes.
- Les ports sont liés à `127.0.0.1`, pour une démo locale seulement. Les secrets du `.env` peuvent être visibles aux personnes autorisées à inspecter Docker : ne pas utiliser des identifiants réels.
- Si une instance InfluxDB 3 existe, les volumes sont séparés ; arrêter ses anciens conteneurs en cas de conflit de nom ou de ports.
- Le `.env` ne doit jamais être commité. Vérifier avec `git status`.

## Modèle de données

Lire [`MODELE_DONNEES.md`](MODELE_DONNEES.md).

## Scripts Python — pas encore migrés

`python/main.py`, `python/simulation.py`, `python/requirements.txt` et `python/.env.example` sont des **archives du code InfluxDB 3** . **Ne pas les exécuter contre InfluxDB 2** : leur SDK, port et SQL ne sont pas compatibles. Ils seront adaptés durant une phase ultérieure.
