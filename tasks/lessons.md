# Leçons

[2026-06-15] | Le `pyproject` listait `websocket>=0.2.1` (paquet PyPI `websocket`, abandonné, sans `WebSocketApp`) alors que le code utilise `websocket.WebSocketApp`. | Pour les WebSockets en Python, toujours utiliser `websocket-client` (importé `import websocket` mais paquet distinct). Vérifier `hasattr(websocket, 'WebSocketApp')` au moindre doute.

[2026-06-15] | `requests` était utilisé dans `finnhub_client.py` sans figurer dans les dépendances. | Déclarer explicitement toute dépendance importée dans `pyproject.toml`, ne pas compter sur les dépendances transitives.

[2026-06-15] | `bitnami/kafka:3.9` introuvable sur Docker Hub (Bitnami a déplacé les anciennes versions). Aussi : les binaires de `apache/kafka` ne sont pas dans le PATH pour `docker exec` (ils sont dans `/opt/kafka/bin/`). | Pour Kafka, utiliser l'image officielle `apache/kafka:X.Y.Z` (env vars `KAFKA_*` sans préfixe CFG) et invoquer les scripts via leur chemin complet `/opt/kafka/bin/...`.

[2026-06-15] | Les `print()` d'un process Python lancé via `timeout ... | head` n'apparaissaient pas (block-buffering quand stdout n'est pas un TTY). | Pour observer les logs d'un process en cours, lancer avec `PYTHONUNBUFFERED=1` (ou `python -u`) et rediriger vers un fichier plutôt que piper dans `head`.
