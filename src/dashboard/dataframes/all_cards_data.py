import pandas as pd
import streamlit as st

from src.dashboard.core import get_connection

@st.cache_data
def load_all_cards_data_df():
    """Load cards with their types aggregated as a list"""
    conn = get_connection()
    query = """
    SELECT 
        c.name AS card_name,
        c.cmc,
        c.image_url AS image_url,
        (SELECT GROUP_CONCAT(DISTINCT type_name) 
         FROM card_types 
         WHERE card_name = c.name) AS card_types,
        (SELECT GROUP_CONCAT(DISTINCT tag_name) 
         FROM card_tags 
         WHERE card_name = c.name) AS card_tags,
        (SELECT GROUP_CONCAT(DISTINCT deck_name) 
         FROM deck_cards 
         WHERE card_name = c.name) AS decks
    FROM cards c
    """
    df = pd.read_sql_query(query, conn)
        
    return df

if __name__ == "__main__":
    pd.set_option('display.max_columns', None)
    df = load_all_cards_data_df()
    # filter to show only cards with card_type: ramp
    ramp_cards = df[df['decks'].str.contains('ramp', na=False)]
    print(ramp_cards[["card_name", "card_types", "card_tags", "decks"]].head())