import streamlit as st
import pandas as pd

from src.dashboard.core import get_connection

@st.cache_data
def load_card_tags_per_deck():
    """Load card tags count per deck"""
    conn = get_connection()
    query = """
    SELECT 
        dc.deck_name,
        ct.tag_name,
        COUNT(*) as tag_count
    FROM deck_cards dc
    JOIN card_tags ct ON dc.card_name = ct.card_name
    GROUP BY dc.deck_name, ct.tag_name
    ORDER BY dc.deck_name, tag_count DESC
    """
    return pd.read_sql_query(query, conn)

card_tags_per_deck_df = load_card_tags_per_deck()