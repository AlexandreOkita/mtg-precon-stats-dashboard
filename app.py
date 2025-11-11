import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="MTG Precon Stats Dashboard",
    page_icon="🧙‍♂️",
    layout="wide"
)

# Database connection
@st.cache_resource
def get_connection():
    return sqlite3.connect("precon.db", check_same_thread=False)

# Data loading functions
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

@st.cache_data
def load_deck_stats():
    """Load tag counts and average CMC per deck"""
    conn = get_connection()
    query = """
    SELECT 
        d.name AS deck_name,
        COUNT(dc.card_name) AS total_cards,
        AVG(c.cmc) AS avg_cmc,
        COUNT(DISTINCT ct.tag_name) AS unique_tags
    FROM decks d
    JOIN deck_cards dc ON d.name = dc.deck_name
    JOIN cards c ON dc.card_name = c.name
    LEFT JOIN card_tags ct ON dc.card_name = ct.card_name
    GROUP BY d.name
    ORDER BY d.name
    """
    return pd.read_sql_query(query, conn)
# App title
st.title("🧙‍♂️ MTG Precon Stats Dashboard")
st.markdown("---")

# Load data
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

# Summary metrics
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

st.markdown("---")

# Main visualizations
tag_filter_tab, deck_analysis_tab = st.tabs(["🔍 Filter by Tag", "📈 Deck Analysis"])

with tag_filter_tab:
    st.header("Filter by Tag - Quantity Across Decks")
    
    if not card_tags_per_deck_df.empty:
        # Create a container to prevent scroll on change
        filter_container = st.container()
        
        with filter_container:
            # Tag selector
            available_tags = sorted(card_tags_per_deck_df['tag_name'].unique())
            selected_tag = st.selectbox(
                "Select a tag to see its distribution across decks:",
                options=available_tags,
                key="tag_filter"
            )
        
        # Filter data for selected tag
        tag_data = card_tags_per_deck_df[card_tags_per_deck_df['tag_name'] == selected_tag].copy()
        
        if not tag_data.empty:
            # Sort by count for better visualization
            tag_data = tag_data.sort_values('tag_count', ascending=False)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Bar chart showing quantity in each deck
                fig_tag_bar = px.bar(
                    tag_data,
                    x='deck_name',
                    y='tag_count',
                    title=f'"{selected_tag}" Cards in Each Deck',
                    labels={'deck_name': 'Deck', 'tag_count': 'Number of Cards'},
                    color='tag_count',
                    color_continuous_scale='Blues'
                )
                fig_tag_bar.update_layout(
                    xaxis_tickangle=-45,
                    showlegend=False
                )
                st.plotly_chart(fig_tag_bar, use_container_width=True)
            
            with col2:
                # Summary metrics
                st.metric("Total Decks with this Tag", len(tag_data))
                st.metric("Total Cards", int(tag_data['tag_count'].sum()))
                st.metric("Average per Deck", f"{tag_data['tag_count'].mean():.1f}")
                st.metric("Max in One Deck", int(tag_data['tag_count'].max()))
            
            # Detailed table
            st.subheader(f"Detailed Breakdown for '{selected_tag}'")
            display_df = tag_data[['deck_name', 'tag_count']].copy()
            display_df.columns = ['Deck', 'Card Count']
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            # Comparison chart - all tags for comparison
            st.subheader("Compare with Other Tags")
            comparison_data = card_tags_per_deck_df.groupby('tag_name')['tag_count'].sum().sort_values(ascending=False).reset_index()
            comparison_data.columns = ['Tag', 'Total Cards']
            
            fig_comparison = px.bar(
                comparison_data,
                x='Tag',
                y='Total Cards',
                title='Total Cards per Tag Across All Decks',
                color='Total Cards',
                color_continuous_scale='Viridis'
            )
            fig_comparison.update_layout(xaxis_tickangle=-45, showlegend=False)
            
            # Highlight selected tag
            fig_comparison.update_traces(
                marker_color=['red' if tag == selected_tag else 'lightblue' for tag in comparison_data['Tag']]
            )
            st.plotly_chart(fig_comparison, use_container_width=True)
        else:
            st.warning(f"No data found for tag: {selected_tag}")
    else:
        st.info("No card tags data available.")

with deck_analysis_tab:
    st.header("Decklist Breakdown")

    
    
    if not deck_stats_df.empty:
        # Create a container to prevent scroll on change
        deck_filter_container = st.container()
        
        with deck_filter_container:
            available_decks = sorted(deck_stats_df['deck_name'].unique())
            selected_deck = st.selectbox(
                "Select a deck to see its details:",
                options=available_decks,
                key="deck_filter"
            )
        
        deck_tag_data = card_tags_per_deck_df[card_tags_per_deck_df['deck_name'] == selected_deck].copy()
        deck_data = deck_stats_df[deck_stats_df['deck_name'] == selected_deck].copy()
        col1, col2 = st.columns([2, 1])

        print("deck_tag_data:\n\n", deck_tag_data)

        with col1:
            # Tag count for selected deck
            fig_tags = px.bar(
                deck_tag_data.sort_values('tag_count', ascending=False),
                x='tag_name',
                y='tag_count',
                title=f'Tag Count in {selected_deck}',
                labels={'tag_name': 'Tag', 'tag_count': 'Count'}
            )
            fig_tags.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_tags, use_container_width=True)
        
        with col2:
            # Deck average CMC - centered
            st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
            st.metric("Average CMC", f"{deck_data['avg_cmc'].values[0]:.2f}")
            st.markdown("</div>", unsafe_allow_html=True)

        # Average CMC per deck
        st.subheader("Compare deck CMC with Other Decks")
        fig_cmc = px.bar(
            deck_stats_df.sort_values('avg_cmc', ascending=False),
            x='deck_name',
            y='avg_cmc',
            title='Average CMC Across All Decks',
            labels={'deck_name': 'Deck', 'avg_cmc': 'Average CMC'}
        )
        fig_cmc.update_traces(
            marker_color=['red' if deck == selected_deck else 'lightblue' for deck in deck_stats_df.sort_values('avg_cmc', ascending=False)['deck_name']]
        )
        fig_cmc.update_layout(xaxis_tickangle=-45, showlegend=False)
        st.plotly_chart(fig_cmc, use_container_width=True)
        
    else:
        st.info("No deck statistics available.")

# Footer
st.markdown("---")
st.markdown("*MTG Precon Stats Dashboard*")
