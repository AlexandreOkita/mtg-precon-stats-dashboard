from pandas import DataFrame
import streamlit as st

def show_summary_metrics(cards_df: DataFrame, decks_df: DataFrame, tags_df: DataFrame, card_tags_df: DataFrame):
    """Display summary metrics in the dashboard."""
    st.header("📊 Summary")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Cards", len(cards_df))
    with col2:
        st.metric("Total Decks", len(decks_df))
    with col3:
        st.metric("Total Tags", len(tags_df))
    with col4:
        st.metric("Unique Tagged Cards", len(card_tags_df['card_name'].unique()))