import sqlite3

# Cria (ou abre) o arquivo do banco
conn = sqlite3.connect("precon.db")
cursor = conn.cursor()

# Cria as tabelas
cursor.executescript("""
CREATE TABLE IF NOT EXISTS cards (
    name TEXT PRIMARY KEY,
    cmc  INTEGER,
    type TEXT
);

CREATE TABLE IF NOT EXISTS decks (
    name TEXT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS tags (
    name TEXT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS deck_cards (
    card_name TEXT NOT NULL,
    deck_name TEXT NOT NULL,
    PRIMARY KEY (card_name, deck_name),
    FOREIGN KEY (card_name) REFERENCES cards(name) ON DELETE CASCADE,
    FOREIGN KEY (deck_name) REFERENCES decks(name) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS card_tags (
    card_name TEXT NOT NULL,
    tag_name TEXT NOT NULL,
    PRIMARY KEY (card_name, tag_name),
    FOREIGN KEY (card_name) REFERENCES cards(name) ON DELETE CASCADE,
    FOREIGN KEY (tag_name) REFERENCES tags(name) ON DELETE CASCADE
);
""")

conn.commit()
print("Banco criado com sucesso ✅")

# # Exemplo de inserções
# cursor.execute("INSERT OR IGNORE INTO cards (name) VALUES (?)", ("Fireball",))
# cursor.execute("INSERT OR IGNORE INTO decks (name) VALUES (?)", ("Mage Deck",))
# cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", ("Spell",))

# # Relacionando o card com o deck e tag
# cursor.execute(
#     "INSERT INTO deck_cards (id, card_name, deck_name) VALUES (?, ?, ?)",
#     (str(uuid4()), "Fireball", "Mage Deck")
# )
# cursor.execute(
#     "INSERT INTO card_tags (card_name, tag_name) VALUES (?, ?)",
#     ("Fireball", "Spell")
# )

# conn.commit()
# print("Dados inseridos com sucesso ✅")

# # Verificação rápida
# for row in cursor.execute("SELECT * FROM deck_cards"):
#     print(row)

conn.close()
