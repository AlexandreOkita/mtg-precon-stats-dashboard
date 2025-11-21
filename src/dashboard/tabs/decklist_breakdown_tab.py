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

        # Card Browser Section
        st.subheader(f"Card Browser - {selected_deck}")
        
        # Get all cards in the selected deck
        all_cards_in_deck = all_cards_df[all_cards_df['decks'].str.contains(selected_deck, na=False)].copy() # type: ignore
        
        # Create filter section in columns
        st.markdown("### Filters")
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        
        with filter_col1:
            # Tag filter
            available_tags = ["All Tags"] + sorted(deck_tag_data['tag_name'].unique())
            selected_tag = st.selectbox(
                "Tag:",
                options=available_tags,
                key="tag_filter_decklist"
            )
        
        with filter_col2:
            # Card type filter
            # Extract all unique card types from the deck
            all_types = set() # type: ignore
            for types_str in all_cards_in_deck['card_types'].dropna():
                all_types.update(types_str.split(','))
            available_types = ["All Types"] + sorted(all_types) # type: ignore
            selected_type = st.selectbox(
                "Card Type:",
                options=available_types,
                key="type_filter_decklist"
            )
        
        with filter_col3:
            # CMC range filter
            min_cmc = int(all_cards_in_deck['cmc'].min())
            max_cmc = int(all_cards_in_deck['cmc'].max())
            cmc_range = st.slider(
                "CMC Range:",
                min_value=min_cmc,
                max_value=max_cmc,
                value=(min_cmc, max_cmc),
                key="cmc_filter_decklist"
            )
        
        # Apply filters
        filtered_cards = all_cards_in_deck.copy()
        
        # Filter by tag
        if selected_tag and selected_tag != "All Tags":
            filtered_cards = filtered_cards[filtered_cards['card_tags'].str.contains(selected_tag, na=False)] # type: ignore
        
        # Filter by card type
        if selected_type and selected_type != "All Types":
            filtered_cards = filtered_cards[filtered_cards['card_types'].str.contains(selected_type, na=False)] # type: ignore
        
        # Filter by CMC range
        filtered_cards = filtered_cards[
            (filtered_cards['cmc'] >= cmc_range[0]) & 
            (filtered_cards['cmc'] <= cmc_range[1])
        ]
        
        # Display filtered results count
        st.write(f"**{len(filtered_cards)} cards found** (out of {len(all_cards_in_deck)} total)")
        
        # Sort options
        sort_col1, sort_col2 = st.columns([1, 3]) # type: ignore
        with sort_col1:
            sort_by = st.selectbox(
                "Sort by:",
                options=["Name", "CMC (Low to High)", "CMC (High to Low)"],
                key="sort_filter_decklist"
            )
        
        # Apply sorting
        if sort_by == "CMC (Low to High)":
            filtered_cards = filtered_cards.sort_values('cmc', ascending=True)
        elif sort_by == "CMC (High to Low)":
            filtered_cards = filtered_cards.sort_values('cmc', ascending=False)
        else:  # Name
            filtered_cards = filtered_cards.sort_values('card_name', ascending=True)
        
        # Display cards as image gallery
        if len(filtered_cards) > 0:
            cols_per_row = 4
            rows = [filtered_cards.iloc[i:i+cols_per_row] for i in range(0, len(filtered_cards), cols_per_row)]
            
            for row in rows:
                cols = st.columns(cols_per_row)
                for idx, (_, card) in enumerate(row.iterrows()):
                    with cols[idx]:
                        if card['image_url'] and card['image_url'].strip():
                            st.image(card['image_url'], use_container_width=True)
                            # Show card details in expander
                            with st.expander("Details"):
                                st.write(f"**CMC:** {card['cmc']}")
                                st.write(f"**Types:** {card['card_types'] or 'N/A'}")
                                st.write(f"**Tags:** {card['card_tags'] or 'N/A'}")
                        else:
                            st.info(f"**{card['card_name']}**\nCMC: {card['cmc']}\n(No image)")
        else:
            st.warning("No cards match the selected filters.")        
    else:
        st.info("No deck statistics available.")