# Orchestration de toute l'infra de la pipeline.
#
# Stacks (3 compose) :
#   kafka/    : Kafka KRaft + Kafka UI
#   infra/    : MinIO (data lake) + producer + consumer conteneurisés
#   airflow/  : Airflow (webserver + scheduler) + Postgres
#
# Usage :
#   make up        # démarre tout
#   make down      # arrête tout
#   make ps        # état des conteneurs
#   make topics    # crée les topics Kafka
#   make logs      # logs du producteur
#   make dashboard # lance le dashboard BI (Streamlit)

KAFKA   = docker compose -f kafka/docker-compose.yml
INFRA   = docker compose -f infra/docker-compose.yml
AIRFLOW = docker compose -f airflow/docker-compose.yml

.PHONY: up down ps topics logs kafka infra airflow airflow-init dashboard clean

## Démarre toute l'infra (ordre : kafka -> minio/producer/consumer -> airflow)
up: kafka topics infra airflow

kafka:
	$(KAFKA) up -d

topics:
	bash kafka/create_topics.sh

infra:
	$(INFRA) up -d --build

airflow-init:
	$(AIRFLOW) up airflow-init

airflow:
	$(AIRFLOW) up -d

## Démarre le dashboard BI (Streamlit -> http://localhost:8501)
dashboard:
	uv run streamlit run dashboard/app.py

## Arrête toute l'infra
down:
	-$(AIRFLOW) down
	-$(INFRA) down
	-$(KAFKA) down

ps:
	@docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' \
	  | grep -E 'kafka|minio|airflow|finhub|postgres' || true

logs:
	$(INFRA) logs -f producer

## Arrêt + suppression des volumes (DONNÉES PERDUES)
clean:
	-$(AIRFLOW) down -v
	-$(INFRA) down -v
	-$(KAFKA) down -v
