from pandas import DataFrame
import streamlit as st
import plotly.express as px

def render_tag_tab(card_tags_per_deck_df: DataFrame):
    st.header("Filter by Tag - Quantity Across Decks")
    
    if not card_tags_per_deck_df.empty:
        
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