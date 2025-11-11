.PHONY: run
run:
	poetry run streamlit run app.py

.PHONY: reset
reset:
	rm -f precon.db
	poetry run python init_db.py
	poetry run python populate_db.py

.PHONY: add-set
add-set:
	poetry run python populate_db.py --set $(SET)

.PHONY: add-deck
add-decks:
	poetry run python populate_db.py --decks $(DECK)

.PHONY: add-decks-only
add-decks-only:
	poetry run python populate_db.py --decks-only