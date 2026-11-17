# Building Monitoring — Projet NoSQL InfluxDB

Démonstration pédagogique de mesures de température et d’humidité provenant de trois capteurs virtuels.

## État du projet

Code d'origine fourni par l'équipe pour InfluxDB 3 Core. **Migration vers InfluxDB 2 envisagée et non encore réalisée.**
Les scripts et la configuration Docker sont conservés pour référence, **non testés dans cette copie**.

## Structure

- `docker-compose.yml` — configuration Docker d'origine (InfluxDB 3 + Explorer)
- `python/main.py` — écriture et lecture
- `python/simulation.py` — simulation des trois capteurs
- `python/requirements.txt` — dépendances Python d'origine
- `python/.env.example` — exemple de configuration sans secrets

## Sécurité

- Ne jamais versionner `python/.env`, `data/`, `plugins/` ou `.venv/`.
- L'archive initiale contenait un token : le révoquer/remplacer avant de réutiliser l'instance.
- Créer un `python/.env` local à partir de `python/.env.example` avec un **nouveau** token pour InfluxDB 3.

## Prochaines étapes

1. Choisir et installer la version InfluxDB cible.
2. Adapter Docker, SDK et requêtes en cas de migration vers InfluxDB 2.
3. Documenter et tester la démonstration CRUD, UI/CLI, Python.
