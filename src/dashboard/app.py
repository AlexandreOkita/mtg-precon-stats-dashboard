import streamlit as st

from src.dashboard.dataframes.card_tags_per_deck_df import load_card_tags_per_deck
from src.dashboard.dataframes.common_dataframes import load_card_tags, load_cards, load_deck_cards, load_decks, load_tags
from src.dashboard.dataframes.deck_stats_df import load_deck_stats
from src.dashboard.tabs.decklist_breakdown_tab import render_decklist_breakdown_tab
from src.dashboard.tabs.tag_tab import render_tag_tab
from src.dashboard.visualizations.summary_metrics import show_summary_metrics

########################
## PAGE CONFIGURATION ##
########################
st.set_page_config(
    page_title="MTG Precon Stats Dashboard",
    page_icon="🧙‍♂️",
    layout="wide"
)
# App title
st.title("🧙‍♂️ MTG Precon Stats Dashboard")
st.markdown("---")

#########################
####### LOAD DATA #######
#########################

try:
    cards_df = load_cards()
    decks_df = load_decks()
    tags_df = load_tags()
    deck_cards_df = load_deck_cards()
    card_tags_df = load_card_tags()
    card_tags_per_deck_df = load_card_tags_per_deck()
    deck_stats_df = load_deck_stats()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

show_summary_metrics(cards_df, decks_df, tags_df, card_tags_df)

st.markdown("---")

tag_filter_tab, deck_analysis_tab = st.tabs(["🔍 Filter by Tag", "📈 Deck Analysis"])

with tag_filter_tab:
    render_tag_tab(card_tags_per_deck_df)

########################
## DECKLIST BREAKDOWN ##
########################

with deck_analysis_tab:
    render_decklist_breakdown_tab(deck_stats_df, card_tags_per_deck_df, deck_cards_df, cards_df)

# Footer
st.markdown("---")
st.markdown("*MTG Precon Stats Dashboard*")
