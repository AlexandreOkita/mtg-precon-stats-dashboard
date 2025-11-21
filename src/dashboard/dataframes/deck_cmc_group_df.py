import streamlit as st
import pandas as pd

from src.dashboard.core import get_connection


@st.cache_data
def load_deck_cmc_group():
    """Load tag counts and average CMC per deck"""
    conn = get_connection()
    query = """
    SELECT 
        d.name AS deck_name,
        c.cmc AS cmc,
        COUNT(DISTINCT dc.card_name) AS total_cards
    FROM decks d
    JOIN deck_cards dc ON d.name = dc.deck_name
    JOIN cards c ON dc.card_name = c.name
    WHERE c.type NOT LIKE '%Land%'
    GROUP BY c.cmc, d.name
    ORDER BY c.cmc;
    """
    return pd.read_sql_query(query, conn)

deck_cmc_group_df = load_deck_cmc_group()

if __name__ == "__main__":
    print(deck_cmc_group_df.head())

# id        deck_name                 total_cards   avg_cmc   unique_tags
# 0         counter_blitz             62            3.314607  9
# 1         counter_intelligence      63            3.444444  9
# 2         desert_bloom              56            3.775000  7
# 3         grand_lacerny             57            3.739726  9
# 4         limit_break               59            3.512500  8