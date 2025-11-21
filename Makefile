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