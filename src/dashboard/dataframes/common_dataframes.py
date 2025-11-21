import streamlit as st
import pandas as pd

from src.dashboard.core import get_connection

@st.cache_data
def load_cards():
    conn = get_connection()
    return pd.read_sql_query("SELECT * FROM cards", conn)

@st.cache_data
def load_decks():
    conn = get_connection()
    return pd.read_sql_query("SELECT * FROM decks", conn)

@st.cache_data
def load_tags():
    conn = get_connection()
    return pd.read_sql_query("SELECT * FROM tags", conn)

@st.cache_data
def load_deck_cards():
    conn = get_connection()
    return pd.read_sql_query("SELECT * FROM deck_cards", conn)

@st.cache_data
def load_card_tags():
    conn = get_connection()
    return pd.read_sql_query("SELECT * FROM card_tags", conn)

cards_df = load_cards()
decks_df = load_decks()
tags_df = load_tags()
deck_cards_df = load_deck_cards()
card_tags_df = load_card_tags()