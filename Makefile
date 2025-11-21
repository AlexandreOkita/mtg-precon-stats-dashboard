.PHONY: run
run:
	PYTHONPATH=. poetry run streamlit run src/dashboard/app.py

.PHONY: reset
reset:
	rm -f precon.db
	PYTHONPATH=. poetry run python src/precon_db/init_db.py
	PYTHONPATH=. poetry run python src/precon_db/populate_db.py

.PHONY: add-set
add-set:
	PYTHONPATH=. poetry run python src/precon_db/populate_db.py --set $(SET)

.PHONY: add-deck
add-decks:
	PYTHONPATH=. poetry run python src/precon_db/populate_db.py --decks $(DECK)

.PHONY: add-decks-only
add-decks-only:
	PYTHONPATH=. poetry run python src/precon_db/populate_db.py --decks-only

.PHONY: prod
prod:
	PYTHONPATH=. poetry run streamlit run src/dashboard/app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true

# Docker commands
.PHONY: docker-build
docker-build:
	docker-compose build

.PHONY: docker-up
docker-up:
	docker-compose up -d

.PHONY: docker-down
docker-down:
	docker-compose down

.PHONY: docker-logs
docker-logs:
	docker-compose logs -f

.PHONY: docker-prod
docker-prod: docker-build docker-up
	@echo "Application running at http://localhost:8501"