import pandas as pd
import streamlit as st

from src.dashboard.core import get_connection

@st.cache_data
def load_cards_with_types():
    """Load cards with their types aggregated as a list"""
    conn = get_connection()
    query = """
    SELECT 
        c.name AS card_name,
        c.cmc,
        c.image_url AS image_url,
        GROUP_CONCAT(ct.type_name, ',') AS card_types,
        GROUP_CONCAT(ctags.tag_name, ',') AS card_tags,
        GROUP_CONCAT(dc.deck_name, ',') AS decks
    FROM cards c
    LEFT JOIN card_types ct ON c.name = ct.card_name
    LEFT JOIN card_tags ctags ON c.name = ctags.card_name
    LEFT JOIN deck_cards dc ON c.name = dc.card_name
    GROUP BY c.name, c.cmc, c.image_url
    """
    df = pd.read_sql_query(query, conn)
        
    return df

if __name__ == "__main__":
    df = load_cards_with_types()
    print(df.head())