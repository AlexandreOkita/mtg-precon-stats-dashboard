.PHONY: run
run:
	poetry run streamlit run app.py

.PHONY: reset
reset:
	rm -f precon.db
	poetry run python init_db.py
	poetry run python populate_db.py