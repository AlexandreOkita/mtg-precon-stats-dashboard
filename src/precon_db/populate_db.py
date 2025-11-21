import sqlite3
import sys
from typing import Optional
from pathlib import Path

import os

from src.external.scryfall_api import ScryfallAPI

# Get project root directory (2 levels up from this file)
PROJECT_ROOT = Path(__file__).parent.parent.parent
DB_PATH = PROJECT_ROOT / "precon.db"

def _insert_card_with_tag(cursor: sqlite3.Cursor, card_name: str, tag_name: str, cmc: int, type_: str, image_url: str) -> None:
    # Insere o card na tabela de cards
    cursor.execute("INSERT OR IGNORE INTO cards (name, cmc, type, image_url) VALUES (?, ?, ?, ?)", (card_name, cmc, type_, image_url))

    # Insere a tag na tabela de tags
    cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag_name,))

    # Relaciona o card com a tag na tabela de card_tags
    cursor.execute(
        "INSERT OR IGNORE INTO card_tags (card_name, tag_name) VALUES (?, ?)",
        (card_name, tag_name)
    )

def _insert_deck_if_card_exists(cursor: sqlite3.Cursor, deck_name: str, card_name: str) -> None:
    # Verifica se o card existe na tabela de cards
    cursor.execute("SELECT 1 FROM cards WHERE name = ?", (card_name,))
    if cursor.fetchone():
        # Insere o deck na tabela de decks
        cursor.execute("INSERT OR IGNORE INTO decks (name) VALUES (?)", (deck_name,))
        
        # Relaciona o card com o deck na tabela de deck_cards
        cursor.execute(
            "INSERT OR IGNORE INTO deck_cards (card_name, deck_name) VALUES (?, ?)",
            (card_name, deck_name)
        )

def _get_tag_list():
    tag_file = PROJECT_ROOT / "tag_list.txt"
    with open(tag_file, "r") as f:
        tags = [line.strip() for line in f.readlines() if line.strip()]
    return tags

def _get_set_list():
    set_file = PROJECT_ROOT / "set_list.txt"
    with open(set_file, "r") as f:
        sets = [line.strip() for line in f.readlines() if line.strip()]
    return sets

def _add_card_type(cursor: sqlite3.Cursor, card_name: str, type_name: str) -> None:
    types = {
        "creature", "instant", "sorcery", "enchantment", "artifact", "planeswalker", "land", "battle"
    }

    type_words = type_name.split()
    for word in type_words:
        if word.lower() in types:
            cursor.execute(
                "INSERT OR IGNORE INTO card_types (card_name, type_name) VALUES (?, ?)",
                (card_name, word.lower())
            )

def populate_db_with_cards(set: Optional[str] = None):
    scryfall_api = ScryfallAPI()
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    def _process_page(card_data): # type: ignore
        if card_data and "data" in card_data:
            for card in card_data["data"]: # type: ignore
                card_name = card["name"] # type: ignore
                cmc = card["cmc"] # type: ignore
                type_ = card["type_line"] # type: ignore
                image_url = card.get("image_uris", {}).get("normal", "")  # type: ignore
                cursor.execute("INSERT OR IGNORE INTO cards (name, cmc, type, image_url) VALUES (?, ?, ?, ?)", (card_name, cmc, type_, image_url)) # type: ignore
                _add_card_type(cursor, card_name, type_)  # type: ignore
            print(f"Inserted cards from set {mtg_set}")
            if "has_more" in card_data and card_data["has_more"]:  # type: ignore
                _process_page(scryfall_api.process_next_page(card_data["next_page"]))  # type: ignore
        else:
            print(f"No cards found for set {mtg_set}")

    if set:
        mtg_sets = [set]
    else:
        mtg_sets = _get_set_list()

    for mtg_set in mtg_sets:
        query = f'set:{mtg_set}'
        card_data = scryfall_api.scryfall_oracle_search(query)  # type: ignore
        _process_page(card_data)

    conn.commit()
    print("Dados inseridos com sucesso ✅")
    conn.close()

def populate_db_with_tags(set: Optional[str] = None):
    scryfall_api = ScryfallAPI()
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    if set:
        mtg_sets = [set]
    else:
        mtg_sets = _get_set_list()

    for mtg_set in mtg_sets:
        for tag_description in _get_tag_list():
            if "->" in tag_description:
                query = f'set:{mtg_set} o:"{tag_description.split("->")[0].strip()}"'
                tag = tag_description.split("->")[1].strip()
            else:
                query = f'set:{mtg_set} otag:"{tag_description}"'
                tag = tag_description
            card_data = scryfall_api.scryfall_oracle_search(query)  # type: ignore

            if card_data and "data" in card_data:
                for card in card_data["data"]: # type: ignore
                    card_name = card["name"] # type: ignore
                    cmc = card["cmc"] # type: ignore
                    type_ = card["type_line"] # type: ignore
                    image_url = card.get("image_uris", {}).get("normal", "")  # type: ignore
                    _insert_card_with_tag(cursor, card_name, tag, cmc, type_, image_url) # type: ignore
                print(f"Inserted cards from set {mtg_set} with tag {tag}")
            else:
                print(f"No cards found for set {mtg_set} with tag {tag}")

    conn.commit()
    print("Dados inseridos com sucesso ✅")

    conn.close()

def populate_db_with_decks(deck: Optional[str] = None):
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    decklists_path = PROJECT_ROOT / "decklists"

    if deck:
        decklists_path = decklists_path / f"{deck}.txt"
    
    # Check all files inside decklists directory
    if os.path.exists(decklists_path):
        for filename in os.listdir(decklists_path):
            file_path = os.path.join(decklists_path, filename)
            if os.path.isfile(file_path):
                clean_filename = filename.rsplit(".", 1)[0]  # Remove file extension for deck name
                print(f"Processing deck file: {clean_filename}")
                with open(file_path, "r") as f:
                    for line in f:
                        card_name = line.split("x ")[-1].split(" (")[0].strip()  # Clean line to get card name
                        if card_name:
                            _insert_deck_if_card_exists(cursor, clean_filename, card_name)  # type: ignore
                print(f"Inserted cards from deck {clean_filename}")
    else:
        print(f"Directory {decklists_path} not found")

    conn.commit()
    print("Dados inseridos com sucesso ✅")

    conn.close()

if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "--set" and len(args) > 1:
        populate_db_with_tags(set=args[1])
    elif args and args[0] == "--decks" and len(args) > 1:
        populate_db_with_decks()
    elif args and args[0] == "--decks-only":
        populate_db_with_decks()
    else:
        populate_db_with_cards()
        populate_db_with_tags()
        populate_db_with_decks()