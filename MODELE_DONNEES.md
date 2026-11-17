# Modélisation — Building Monitoring

- **Organisation** : `eseo`
- **Bucket InfluxDB 2** : `building_monitoring` (rétention : valeur par défaut, illimitée)
- **Measurement** : `room_climate`
- **Tags** : `room` (`salle_101` / `salle_102` / `salle_103`), `sensor_id` (`CAP-01` / `CAP-02` / `CAP-03`)
- **Fields** : `temperature` (float, °C), `humidity` (float, %)
- **Timestamp** : date/heure UTC de la mesure, spécifié explicitement pour les données de test CRUD.

Exemple Line Protocol 

```text
room_climate,room=salle_101,sensor_id=CAP-01 temperature=23.0,humidity=48.0
```

Un `point` est identifié par measurement, ensemble de tags et timestamp. Les fields contiennent les valeurs mesurées. Ne pas utiliser le timestamp comme tag.


