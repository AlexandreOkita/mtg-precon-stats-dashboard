from pandas import DataFrame
import streamlit as st
import plotly.express as px

def render_decklist_breakdown_tab(deck_stats_df: DataFrame, card_tags_per_deck_df: DataFrame, deck_cards_df: DataFrame, cards_df: DataFrame, all_cards_df: DataFrame):
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
            # Total cards in deck
            st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
            st.metric("Total No Land Cards", deck_data['total_cards'].values[0])
            st.markdown("</div>", unsafe_allow_html=True)

            # Deck average CMC - centered
            st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
            st.metric("Average CMC", f"{deck_data['avg_cmc'].values[0]:.2f}")
            st.markdown("</div>", unsafe_allow_html=True)


        st.subheader(f"Cards grouped by CMC in {selected_deck}")
        fig_cmc_cards_deck = px.histogram(
            deck_cards_df.merge(cards_df, left_on='card_name', right_on='name')[deck_cards_df['deck_name'] == selected_deck],
            x='cmc',
            title=f'CMC Distribution in {selected_deck}',
            labels={'cmc': 'Converted Mana Cost', 'count': 'Number of Cards'},
            nbins=15
        )
        st.plotly_chart(fig_cmc_cards_deck, use_container_width=True)

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

        # Table with all cards in deck
        st.subheader(f"All Cards in {selected_deck}")
        available_tags = ["All Tags"] + sorted(deck_tag_data['tag_name'].unique())
        selected_tag = st.selectbox(
                "Select a tag to filter by:",
                options=available_tags,
                key="tag_filter_decklist"
            )
        all_cards_in_deck = all_cards_df[all_cards_df['decks'].str.contains(selected_deck, na=False)] # type: ignore
        if selected_tag and selected_tag != "All Tags":
            all_cards_in_deck = all_cards_in_deck[all_cards_in_deck['card_tags'].str.contains(selected_tag, na=False)] # type: ignore
        
        # Display cards as image gallery
        st.write(f"**{len(all_cards_in_deck)} cards found**")
        
        # Create a grid layout with 4 columns
        cols_per_row = 4
        rows = [all_cards_in_deck.iloc[i:i+cols_per_row] for i in range(0, len(all_cards_in_deck), cols_per_row)]
        
        for row in rows:
            cols = st.columns(cols_per_row)
            for idx, (_, card) in enumerate(row.iterrows()):
                with cols[idx]:
                    if card['image_url'] and card['image_url'].strip():
                        st.image(card['image_url'], use_container_width=True)
                    else:
                        st.info(f"**{card['card_name']}**\nCMC: {card['cmc']}\n(No image)")        
    else:
        st.info("No deck statistics available.")