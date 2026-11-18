# Building Monitoring — Projet NoSQL avec InfluxDB 2

Projet pédagogique de surveillance d'un bâtiment composé de trois salles. Des capteurs virtuels mesurent la température et l'humidité, envoient les points à **InfluxDB 2**, puis les données sont consultées et analysées avec **Flux**, l'interface Web et le SDK Python.


## 1. Objectifs

Le projet consiste à simuler un système de monitoring composé de trois salles :

| Salle | Capteur | Température de base | Humidité de base |
|---|---|---:|---:|
| salle_101 | CAP-01 | 22 °C | 45 % |
| salle_102 | CAP-02 | 25 °C | 52 % |
| salle_103 | CAP-03 | 21 °C | 48 % |

Chaque capteur produit périodiquement deux mesures : la température en degrés Celsius et l'humidité relative en pourcentage.

Les objectifs techniques sont de :

- déployer InfluxDB 2 avec Docker Compose ;
- comprendre le modèle de données d'une base de séries temporelles ;
- écrire et lire des mesures depuis Python avec le SDK InfluxDB 2 ;
- simuler plusieurs capteurs et envoyer automatiquement leurs données ;
- interroger les données avec Flux ;
- calculer des indicateurs temporels et repérer des dépassements de température ;
- démontrer les opérations CRUD avec l'interface graphique et la ligne de commande (CLI).

## 2. Architecture

```text
       CAP-01             CAP-02             CAP-03
     salle_101          salle_102          salle_103
          \                 |                  /
           +----------------+-----------------+
                            |
                            v
                  +-------------------+
                  | Python            |
                  | simulation.py     |
                  +-------------------+
                            |
                     SDK Python 2.x
                            |
                            v
                 +----------------------+
                 | InfluxDB 2           |
                 | Docker               |
                 |                      |
                 | Organisation : eseo |
                 | Bucket :             |
                 | building_monitoring  |
                 +----------------------+
                     ^             ^
                     |             |
               Requêtes Flux    Data Explorer
                     |          Interface Web
                     v             |
               +------------+      |
               | analyse.py |      |
               | main.py    |      |
               +------------+      |
                                   |
                         CLI InfluxDB / PowerShell
                         (démonstration CRUD)
```

**Rôle des composants :**

- **Docker Compose** démarre InfluxDB 2 et conserve ses données dans des volumes Docker.
- **InfluxDB 2** stocke les points de mesure horodatés.
- **`simulation.py`** génère les valeurs des trois capteurs et les écrit dans InfluxDB toutes les 10 secondes.
- **`main.py`** effectue un test ponctuel d'écriture et de lecture via le SDK Python.
- **`analyse.py`** exécute des requêtes Flux pour calculer des statistiques et détecter les températures supérieures à 30 °C.
- **Data Explorer** permet de consulter les mesures, d'écrire des points en Line Protocol et d'exécuter des requêtes Flux.
- **La CLI InfluxDB** permet notamment d'écrire, lire et supprimer des points depuis PowerShell.

## 3. Technologies

| Technologie | Utilisation |
|---|---|
| InfluxDB 2 | Base de données de séries temporelles |
| Docker / Docker Compose | Déploiement local d'InfluxDB |
| Python 3 | Simulation, écriture, lecture et analyse |
| `influxdb-client` | SDK Python pour InfluxDB 2 |
| `python-dotenv` | Chargement des paramètres depuis `.env` |
| Flux | Langage de requête utilisé par InfluxDB 2 |


## 4. Modèle de données

### 4.1 Organisation, bucket et measurement

| Élément | Valeur | Rôle |
|---|---|---|
| Organisation | `eseo` | Regroupe les ressources InfluxDB |
| Bucket | `building_monitoring` | Espace de stockage des données temporelles |
| Measurement | `room_climate` | Type de mesure : climat des salles |

Dans InfluxDB 2, un **bucket** est l'espace dans lequel les données temporelles sont stockées. Une **measurement** identifie la famille de mesures.

### 4.2 Tags, fields et timestamp

| Élément | Nom | Exemple | Rôle |
|---|---|---|---|
| Tag | `room` | `salle_101` | Identifie la salle |
| Tag | `sensor_id` | `CAP-01` | Identifie le capteur |
| Field | `temperature` | `23.0` | Température en °C |
| Field | `humidity` | `48.0` | Humidité en % |
| Timestamp | `time` | Date/heure UTC | Date de la mesure |

Les **tags** décrivent le contexte du point et facilitent le filtrage et le regroupement. Les **fields** contiennent les valeurs réellement mesurées. Le **timestamp** indique à quel moment le point a été observé.

### 4.3 Line Protocol

Le Line Protocol est le format texte utilisé pour écrire un point dans InfluxDB. Exemple du projet :

```text
room_climate,room=salle_101,sensor_id=CAP-01 temperature=23.0,humidity=48.0
```

Cette ligne contient :

- `room_climate` : measurement ;
- `room=salle_101` et `sensor_id=CAP-01` : tags ;
- `temperature=23.0` et `humidity=48.0` : fields ;
- aucun timestamp explicite : InfluxDB attribue alors l'heure de réception au point.

Pour fixer le timestamp, on l'ajoute à la fin de la ligne et on indique sa précision lors de l'écriture. Le scénario CRUD de ce README utilise un timestamp fixe en secondes.

### 4.4 Données simulées

Les valeurs évoluent légèrement à chaque cycle. Dans `simulation.py`, une anomalie pédagogique est injectée sur le capteur `CAP-02` des cycles 6 à 9 : une hausse de 8 °C est ajoutée à la température générée. Cela permet de tester la détection des dépassements de 30 °C.

Le modèle détaillé est également décrit dans [`MODELE_DONNEES.md`](MODELE_DONNEES.md).

## 5. Structure du dépôt

```text
influxdb-building-monitoring/
│
├── docker-compose.yml          # Démarrage d'InfluxDB 2
├── .env.example                # Modèle de configuration sans secret
├── .gitignore                  # Fichiers exclus de Git
├── README.md                   # Documentation principale
├── MODELE_DONNEES.md           # Description du modèle temporel
├── CRUD_DEMO.md                # Scénario CRUD détaillé
│
└── python/
    ├── requirements.txt        # Dépendances Python
    ├── main.py                 # Test ponctuel : écriture et lecture
    ├── simulation.py           # Simulation continue des trois capteurs
    └── analyse.py               # Analyses temporelles avec Flux
```

L'environnement virtuel `.venv/` et le fichier `.env` sont créés localement et ne sont pas versionnés.

## 6. Prérequis

Installer les outils suivants :

- Docker Desktop, démarré ;
- Git ;
- Python 3 ;
- PowerShell ou un terminal équivalent ;
- un navigateur Web.

Vérifier les installations :

```powershell
docker --version
docker compose version
py --version
git --version
```

## 7. Installation et configuration

### 7.1 Récupérer le dépôt

```powershell
git clone https://github.com/DiarraMaim01influxdb-building-monitoring.git
cd influxdb-building-monitoring
```


### 7.2 Créer le fichier `.env`

À la racine du dépôt, copier le modèle :

```powershell
Copy-Item .env.example .env
```

Ouvrir `.env` et renseigner les valeurs locales :

```dotenv
INFLUX_USERNAME=admin
INFLUX_PASSWORD=REMPLACER_PAR_UN_MOT_DE_PASSE_FORT
INFLUX_ORG=eseo
INFLUX_BUCKET=building_monitoring
INFLUX_TOKEN=REMPLACER_PAR_UN_TOKEN_LONG_ET_ALEATOIRE
```



Le code Python utilise par défaut `http://localhost:8086`. Il est possible de préciser l'URL dans `.env` :

```dotenv
INFLUX_URL=http://localhost:8086
```


### 7.3 Créer l'environnement virtuel Python

Depuis la racine du dépôt :

```powershell
py -m venv .venv
```

Activer l'environnement :

```powershell
.\.venv\Scripts\Activate.ps1
```


Il est également possible d'utiliser directement l'interpréteur de l'environnement virtuel sans l'activer :

```powershell
.\.venv\Scripts\python.exe -m pip install -r python\requirements.txt
```

### 7.4 Installer les dépendances

Avec l'environnement activé :

```powershell
python -m pip install --upgrade pip
python -m pip install -r python\requirements.txt
```

Les bibliothèques déclarées dans `python/requirements.txt` sont :

- `influxdb-client` : client Python pour InfluxDB 2 ;
- `python-dotenv` : chargement des variables du fichier `.env`.

## 8. Démarrer InfluxDB

Depuis la racine du dépôt :

```powershell
docker compose up -d
```

Ouvrir l'interface graphique :

<http://localhost:8086>

Se connecter avec les identifiants configurés dans `.env` lors de l'initialisation.

## 9. Exécuter les scripts Python

Les commandes ci-dessous sont données depuis la racine du dépôt. Si `.venv` est activé, utiliser `python`. Sinon, utiliser `.\.venv\Scripts\python.exe`.

### 9.1 Test ponctuel — `main.py`

```powershell
python python\main.py
```

Ce script :

1. charge les paramètres depuis `.env` ;
2. crée un client `InfluxDBClient` ;
3. construit un point `room_climate` avec les tags `room` et `sensor_id` ;
4. ajoute les fields `temperature` et `humidity` ;
5. écrit le point dans le bucket ;
6. exécute une requête Flux pour afficher les cinq dernières températures de la dernière heure.

Il sert à vérifier rapidement l'authentification, l'écriture et la lecture via le SDK Python.

### 9.2 Simulation continue — `simulation.py`

```powershell
python python\simulation.py
```

Le programme génère une mesure pour chacun des trois capteurs, écrit les points dans InfluxDB puis attend 10 secondes avant le cycle suivant.

Exemple de sortie :

```text
Simulation lancée : 3 capteurs, envoi toutes les 10 secondes. CTRL+C pour arrêter.
salle_101 | CAP-01 | 22.31 °C | 44.25 %
salle_102 | CAP-02 | 24.72 °C | 53.14 %
salle_103 | CAP-03 | 20.84 °C | 47.22 %
Cycle 1 écrit avec succès. Prochain envoi dans 10 s.
```

Arrêter la simulation avec `Ctrl+C`.

### 9.3 Analyse temporelle — `analyse.py`

```powershell
python python\analyse.py
```

Le script interroge la measurement `room_climate` sur les **sept derniers jours** et affiche :

1. la température moyenne par salle et capteur (`mean`) ;
2. la température maximale par salle et capteur (`max`) ;
3. les mesures dont la température dépasse 30 °C.

Les requêtes utilisent Flux et filtrent le field `temperature`.

Si le script affiche « Aucune mesure trouvée sur les 7 derniers jours », vérifier que le serveur est démarré, que le bucket et le token sont corrects, puis lancer `simulation.py` pendant plusieurs cycles. Arrêter la simulation avec `Ctrl+C` et relancer `analyse.py`.

Les dépassements apparaissent lorsque les cycles 6 à 9 de `CAP-02` ont été exécutés au cours de la période analysée.

## 10. Explorer les données dans l'interface

1. Ouvrir <http://localhost:8086>.
2. Accéder à **Data Explorer**.
3. Sélectionner le bucket `building_monitoring`.
4. Ouvrir **Script Editor**.
5. Coller une requête Flux puis cliquer sur **Submit**.

Exemple : afficher les températures des trois salles sur les dernières 24 heures :

```flux
from(bucket: "building_monitoring")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "room_climate")
  |> filter(fn: (r) => r._field == "temperature")
  |> group(columns: ["room", "sensor_id"])
```

Exemple : calculer la température moyenne par salle :

```flux
from(bucket: "building_monitoring")
  |> range(start: -7d)
  |> filter(fn: (r) => r._measurement == "room_climate")
  |> filter(fn: (r) => r._field == "temperature")
  |> group(columns: ["room", "sensor_id"])
  |> mean()
```

## 11. Démonstration CRUD — interface graphique et CLI

Cette démonstration présente les quatre opérations **Create, Read, Update, Delete** sur une measurement isolée appelée `crud_demo`. Elle ne modifie pas les mesures des capteurs dans `room_climate`.

Le scénario est réalisable avec les deux moyens d'interaction suivants :

- **Interface graphique** : InfluxDB Web UI, notamment **Load Data** et **Data Explorer**.
- **CLI** : PowerShell exécute les commandes `influx write`, `influx query` et `influx delete` à l'intérieur du conteneur Docker.


### 11.1 CREATE — insérer un point

#### Depuis l'interface graphique

1. Ouvrir <http://localhost:8086> et se connecter.
2. Dans le menu de navigation, ouvrir **Load Data → Buckets**.
3. Sur le bucket `building_monitoring`, cliquer sur **Add Data → Line Protocol**.
4. Choisir **Enter Manually**.
5. Vérifier que le bucket sélectionné est `building_monitoring`.
6. Dans la liste **Precision**, sélectionner **Seconds**, car le timestamp fourni est exprimé en secondes Unix.
7. Coller la ligne suivante dans la zone Line Protocol :

```text
crud_demo,room=salle_101,sensor_id=TEST-01 temperature=35.5,humidity=60.0 1794916800
```

8. Cliquer sur **Write Data**. L'interface doit confirmer l'écriture.

#### Depuis la CLI

Dans PowerShell, toujours à la racine du dépôt :

```powershell
docker exec -e "INFLUX_TOKEN=$env:INFLUX_TOKEN" building-monitoring-influxdb2 influx write --bucket building_monitoring --org eseo --precision s "crud_demo,room=salle_101,sensor_id=TEST-01 temperature=35.5,humidity=60.0 1794916800"
```

La CLI peut ne rien afficher en cas de succès : il faut vérifier avec une lecture.

#### Décomposition du point

| Élément | Valeur |
|---|---|
| Measurement | `crud_demo` |
| Tag `room` | `salle_101` |
| Tag `sensor_id` | `TEST-01` |
| Field `temperature` | `35.5` |
| Field `humidity` | `60.0` |
| Timestamp | `1794916800` secondes Unix |

### 11.2 READ — lire le point

#### Depuis l'interface graphique

1. Ouvrir **Data Explorer**.
2. Sélectionner **Script Editor**.
3. Coller la requête Flux :

```flux
from(bucket: "building_monitoring")
  |> range(start: 2026-11-17T00:00:00Z, stop: 2026-11-19T00:00:00Z)
  |> filter(fn: (r) => r._measurement == "crud_demo")
  |> filter(fn: (r) => r.sensor_id == "TEST-01")
  |> yield(name: "result")
```

4. Cliquer sur **Submit**.
5. Activer **View Raw Data** pour afficher les résultats sous forme de lignes `_field` / `_value`.

Résultat attendu après CREATE :

- `temperature = 35.5`
- `humidity = 60.0`

#### Depuis la CLI

```powershell
docker exec -e "INFLUX_TOKEN=$env:INFLUX_TOKEN" building-monitoring-influxdb2 influx query 'from(bucket: "building_monitoring") |> range(start: 2026-11-17T00:00:00Z, stop: 2026-11-19T00:00:00Z) |> filter(fn: (r) => r._measurement == "crud_demo" and r.sensor_id == "TEST-01")'
```

La requête utilise des bornes temporelles explicites. Il ne faut pas se fier au sélecteur rapide « Past 15m » de l'interface pour ce point daté.

### 11.3 UPDATE — corriger la température


InfluxDB 2 ne propose pas un `UPDATE ... SET ... WHERE` de type SQL relationnel pour modifier un point. Pour ce scénario, on **réécrit le point** en conservant exactement la même measurement, le même jeu de tags et le même timestamp. InfluxDB fusionne les fields : une valeur réécrite remplace le field correspondant, tandis que les fields non réécrits sont conservés.

#### Depuis l'interface graphique

1. Ouvrir **Load Data → Buckets**.
2. Sur `building_monitoring`, choisir **Add Data → Line Protocol**.
3. Sélectionner **Enter Manually** et vérifier la précision **Seconds**.
4. Coller la ligne de réécriture :

```text
crud_demo,room=salle_101,sensor_id=TEST-01 temperature=24.0 1794916800
```

5. Cliquer sur **Write Data**.
6. Revenir dans **Data Explorer** et relancer la requête READ de la section précédente.

#### Depuis la CLI

```powershell
docker exec -e "INFLUX_TOKEN=$env:INFLUX_TOKEN" building-monitoring-influxdb2 influx write --bucket building_monitoring --org eseo --precision s "crud_demo,room=salle_101,sensor_id=TEST-01 temperature=24.0 1794916800"
```

Relancer la requête READ. Résultat attendu :

- `temperature = 24.0` : la valeur a été remplacée ;
- `humidity = 60.0` : le field non réécrit est conservé.



### 11.4 DELETE — supprimer le point de test

Dans InfluxDB 2, il n'y a pas de commande Data Explorer permettant de supprimer simplement un point isolé en cliquant sur une ligne. Pour cette démonstration, la suppression ciblée est réalisée avec la **CLI** (ou l'API). L'interface graphique sert ensuite à vérifier que le point n'est plus retourné.

#### Depuis la CLI

```powershell
docker exec -e "INFLUX_TOKEN=$env:INFLUX_TOKEN" building-monitoring-influxdb2 influx delete --bucket building_monitoring --org eseo --start 2026-11-17T11:59:59Z --stop 2026-11-17T12:00:01Z --predicate '_measurement="crud_demo" AND sensor_id="TEST-01"'
```

La suppression est limitée à une courte fenêtre autour du timestamp du point et à la measurement `crud_demo` avec le tag `sensor_id=TEST-01`.



#### Vérifier la suppression dans l'interface graphique

1. Revenir dans **Data Explorer → Script Editor**.
2. Relancer la requête READ de la section 11.3.
3. Le résultat attendu est **No Results**.

#### Vérifier également avec la CLI

Relancer la requête `influx query` de la section 11.2 : elle ne doit plus retourner de point `crud_demo` avec `sensor_id=TEST-01` dans la fenêtre temporelle choisie.

### 11.5 Tableau récapitulatif : quelle opération avec quel outil ?

| Opération | Interface graphique | CLI |
|---|---|---|
| **Create** | Oui — Load Data → Buckets → Add Data → Line Protocol | Oui — `influx write` |
| **Read** | Oui — Data Explorer et requête Flux | Oui — `influx query` |
| **Update** | Oui, indirectement — réécriture en Line Protocol avec les mêmes tags et timestamp | Oui — `influx write` avec le même point |
| **Delete** | Pas de suppression ciblée d'un point depuis Data Explorer dans ce scénario ; l'interface sert à vérifier le résultat | Oui — `influx delete` avec une fenêtre et un prédicat |

La démonstration compare ainsi les deux moyens d'accès sans laisser penser que l'interface graphique possède un bouton CRUD universel. La suppression ciblée est faite par la CLI, puis vérifiée dans l'interface.

## 12. Analyses temporelles

Le script `analyse.py` illustre trois traitements :

- **Moyenne** : résumer la température observée par salle et capteur ;
- **Maximum** : identifier la température la plus élevée observée ;
- **Détection de dépassement** : repérer les mesures supérieures à 30 °C.

Les résultats dépendent des données réellement présentes dans le bucket et de la période analysée. Les valeurs du simulateur sont variables ; les résultats exacts peuvent donc changer d'une exécution à l'autre.

## 16. Documentation officielle

- [InfluxDB 2 — écrire des données avec l'interface et Line Protocol](https://docs.influxdata.com/influxdb/v2/get-started/write/)
- [Référence du Line Protocol InfluxDB 2](https://docs.influxdata.com/influxdb/v2/reference/syntax/line-protocol/)
- [CLI InfluxDB — write](https://docs.influxdata.com/influxdb/v2/reference/cli/influx/write/)
- [CLI InfluxDB — query](https://docs.influxdata.com/influxdb/v2/reference/cli/influx/query/)
- [CLI InfluxDB — delete](https://docs.influxdata.com/influxdb/v2/reference/cli/influx/delete/)
- [InfluxDB 2 — gérer les points dupliqués](https://docs.influxdata.com/influxdb/v2/write-data/best-practices/duplicate-points/)
- [InfluxDB 2 — supprimer des données](https://docs.influxdata.com/influxdb/v2/write-data/delete-data/)
- [Client Python InfluxDB](https://github.com/influxdata/influxdb-client-python)

---

**Projet réalisé dans le cadre du cours NoSQL à l'ESEO.**

**Sujet :** Building Monitoring — surveillance temporelle de la température et de l'humidité de trois salles avec InfluxDB 2 et Python.
