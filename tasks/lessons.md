# Leçons

[2026-06-15] | Le `pyproject` listait `websocket>=0.2.1` (paquet PyPI `websocket`, abandonné, sans `WebSocketApp`) alors que le code utilise `websocket.WebSocketApp`. | Pour les WebSockets en Python, toujours utiliser `websocket-client` (importé `import websocket` mais paquet distinct). Vérifier `hasattr(websocket, 'WebSocketApp')` au moindre doute.

[2026-06-15] | `requests` était utilisé dans `finnhub_client.py` sans figurer dans les dépendances. | Déclarer explicitement toute dépendance importée dans `pyproject.toml`, ne pas compter sur les dépendances transitives.

[2026-06-15] | `bitnami/kafka:3.9` introuvable sur Docker Hub (Bitnami a déplacé les anciennes versions). Aussi : les binaires de `apache/kafka` ne sont pas dans le PATH pour `docker exec` (ils sont dans `/opt/kafka/bin/`). | Pour Kafka, utiliser l'image officielle `apache/kafka:X.Y.Z` (env vars `KAFKA_*` sans préfixe CFG) et invoquer les scripts via leur chemin complet `/opt/kafka/bin/...`.

[2026-06-15] | Les `print()` d'un process Python lancé via `timeout ... | head` n'apparaissaient pas (block-buffering quand stdout n'est pas un TTY). | Pour observer les logs d'un process en cours, lancer avec `PYTHONUNBUFFERED=1` (ou `python -u`) et rediriger vers un fichier plutôt que piper dans `head`.

[2026-06-15] | Toujours vérifier l'arborescence cible dans `architecture-projet.md` AVANT de créer un dossier. J'avais créé `storage/` pour MinIO alors que l'archi le veut dans `infra/`. | Avant de créer un nouveau répertoire de premier niveau, le confronter à `architecture-projet.md` ; ne pas inventer de structure.

[2026-06-15] | MinIO renvoie `XMinioStorageFull` (refus d'écriture) quand le disque hôte passe sous son seuil de sécurité — ce n'était pas un bug du code consumer. | Devant une erreur S3/MinIO inattendue, vérifier `df -h` en premier. Récupérer de l'espace via `docker builder prune -af` est sans risque.

[2026-06-15] | Dans un `resample(...).agg(col=(c, lambda s: ...))`, le lambda ne reçoit QUE la série de la colonne agrégée : `g.loc[s.index, 'autre_col']` ne s'aligne pas et donne des résultats faux (VWAP 5min = 1.6M au lieu de 65k). | Pour une agrégation multi-colonnes par fenêtre (ex. VWAP = prix pondéré par volume), utiliser `resample(...).apply(fn)` où `fn(window_df)` reçoit tout le sous-DataFrame de la fenêtre.

[2026-06-15] | Un message de test injecté manuellement (symbol 'TEST', timestamp en secondes) a pollué tout le pipeline jusqu'au Gold (epoch s pris pour ms -> date 1970). | Ne pas injecter de données de test dans les topics/buckets réels. Si nécessaire, utiliser un symbole/préfixe dédié et nettoyer après.

[2026-06-15] | Airflow en Docker : 3 pièges au lancement. (1) PermissionError sur /opt/airflow/logs -> définir `user: "<UID_hôte>:0"` + chown du dossier. (2) `getpwuid uid not found` -> NE PAS override `entrypoint`, passer la commande via l'entrypoint officiel (il crée l'entrée passwd). (3) deps projet absentes -> `_PIP_ADDITIONAL_REQUIREMENTS`. | Toujours vérifier `docker ps` pour les ports déjà pris (8081 l'était) avant de mapper.

[2026-06-15] | Depuis un conteneur, joindre Kafka via la gateway hôte (advertised `localhost:9092`) donne ECONNREFUSED : le broker renvoie une adresse advertised non joignable. | Mettre les conteneurs sur un réseau docker partagé (réseaux `external`) et utiliser le listener INTERNAL (`kafka:29092`, `minio:9000`). Plus fiable que host.docker.internal sur Linux.

[2026-06-15] | KafkaConsumer en mode batch borné (run_once) : avec un consumer_timeout_ms court, le 1er poll déclenche un rebalance plus long que le timeout -> RebalanceInProgressError, 0 message. | Faire un `consumer.poll(timeout_ms=3000)` initial pour forcer l'assignation des partitions avant la boucle d'itération, et traiter les messages déjà renvoyés.

[2026-06-15] | Recréer le conteneur Kafka (changement de config listeners) a réinitialisé le cluster KRaft -> topics perdus, et le groupe consumer avait des offsets avancés (LAG=0) suite aux tests en échec. | Après recreate Kafka : relancer create_topics.sh. Pour rejouer une consommation : reset offsets `kafka-consumer-groups.sh --reset-offsets --to-earliest --execute`.

[2026-06-15] | dbt-core ne supporte pas Python 3.14 (crash mashumaro UnserializableField). Et un venv n'est pas portable hôte<->conteneur (pyvenv.cfg pointe l'interpréteur en absolu). | Isoler dbt dans un venv py3.12 dédié pour l'usage local ; pour Airflow, installer dbt-duckdb dans l'image et l'appeler via `python -m dbt.cli.main` (pas le venv hôte monté).

[2026-06-15] | dbt-duckdb peut lire un data lake S3/MinIO directement via l'extension httpfs (read_parquet('s3://...')), sans charger les données. Profil : settings s3_endpoint (host:port sans schéma), s3_url_style=path, s3_use_ssl=false. | Bonne alternative gratuite/locale à Snowflake pour la modélisation dbt sur des Parquet.
