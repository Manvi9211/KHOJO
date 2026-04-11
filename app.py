"""
Khojo: Professional Fashion Product Recommender System
A Streamlit application for discovering similar fashion products using TF-IDF similarity.

Author: Your Name
Version: 2.0
"""

import os
import streamlit as st
import pandas as pd
from pathlib import Path
from data_loader import DataLoader
from recommender import RecommendationEngine
from ui_components import (
    apply_custom_styling,
    display_product_card,
    display_stats_boxes,
    get_main_search_filters,
    display_no_results
)
from favorites_manager import FavoritesManager
from search_history import SearchHistoryManager


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Khojo - Fashion Recommender",
    page_icon="chart_with_upwards_trend",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_custom_styling()


# ============================================================================
# INITIALIZATION
# ============================================================================

def _normalize_dataset_url(url: str) -> str:
    """Convert common share links (Google Drive view link) to direct-download URL."""
    cleaned = (url or '').strip()
    if 'drive.google.com/file/d/' in cleaned:
        try:
            file_id = cleaned.split('/file/d/')[1].split('/')[0]
            return f"https://drive.google.com/uc?export=download&id={file_id}"
        except Exception:
            return cleaned
    return cleaned


@st.cache_resource
def load_data():
    """Load and cache the dataset from local file path or URL."""
    try:
        # 1) Local candidates inside repo/runtime
        dataset_candidates = [
            Path("myntra202305041052.csv"),
            Path("myntra.csv"),
            Path("data/myntra202305041052.csv"),
            Path("data/myntra.csv"),
        ]

        # 2) Optional path from environment/secrets (works on Streamlit Cloud)
        env_dataset_path = os.getenv("DATASET_PATH", "").strip()
        if env_dataset_path:
            dataset_candidates.insert(0, Path(env_dataset_path))

        secret_dataset_path = str(st.secrets.get("DATASET_PATH", "")).strip()
        if secret_dataset_path:
            dataset_candidates.insert(0, Path(secret_dataset_path))

        csv_source = next((str(path)
                          for path in dataset_candidates if path.exists()), None)

        # 3) Optional URL fallback from environment/secrets
        if csv_source is None:
            env_dataset_url = os.getenv("DATASET_URL", "").strip()
            secret_dataset_url = str(st.secrets.get("DATASET_URL", "")).strip()
            dataset_url = env_dataset_url or secret_dataset_url

            if dataset_url:
                dataset_url = _normalize_dataset_url(dataset_url)
                if dataset_url:
                    csv_source = dataset_url
                    st.info(f"Loading from URL: {dataset_url[:80]}...")

        if csv_source is None:
            raise FileNotFoundError(
                "Dataset not found. Provide one of: "
                "myntra.csv in repo root, DATASET_PATH, or DATASET_URL in Streamlit secrets."
            )

        loader = DataLoader(csv_path=csv_source, sample_size=10000)
        return loader.get_dataframe(), loader.get_stats()
    except FileNotFoundError as e:
        st.error(
            f"Dataset not found. Error: {str(e)}\n\n"
            "Solutions:\n"
            "1. Add myntra.csv to repo root\n"
            "2. Set DATASET_PATH in Streamlit secrets\n"
            "3. Set DATASET_URL in Streamlit secrets"
        )
        st.stop()
    except Exception as e:
        st.error(f"Error loading dataset: {str(e)}")
        st.stop()
        st.stop()


@st.cache_resource
        def create_recommender(df):
        """Create and cache the recommendation engine."""
        engine = RecommendationEngine(df)
        return engine

        # Load data
        df, stats = load_data()

        # Create recommender (clear cache to get latest version)
        try:
        st.cache_resource.clear()
        except:
        pass

        recommender = create_recommender(df)
        FavoritesManager.initialize_session()
        SearchHistoryManager.initialize()

        # Initialize session state for navigation
        if 'show_favorites' not in st.session_state:
        st.session_state.show_favorites = False
        if 'search_executed' not in st.session_state:
        st.session_state.search_executed = False
        if 'last_search' not in st.session_state:
        st.session_state.last_search = {}

        # ============================================================================
        # HEADER SECTION
        # ============================================================================

        st.markdown("""
<div style="text-align: center; margin-bottom: 2rem;">
    <h1>Khojo</h1>
    <p style="color: #666; font-size: 1.1rem;">Discover Fashion Products Tailored to Your Style</p>
</div>
""", unsafe_allow_html=True)

        # Display dataset statistics (hidden)
        # with st.expander("Dataset Overview", expanded=False):
        #     display_stats_boxes(stats)

        # ============================================================================
        # SIDEBAR - PROFILE & SAVED ITEMS
        # ============================================================================

        with st.sidebar:
        favorites = FavoritesManager.get_favorites()
        db_stats = FavoritesManager.get_database_stats()
        profile = SearchHistoryManager.get_user_style_profile()

        st.markdown("---")
        st.markdown("### Your Style Profile")

        if profile['has_profile']:
        st.metric("Average Budget", f"Rs {profile['average_budget']:,.0f}")
        budget_min, budget_max = profile['budget_range']
        st.caption(f"Range: Rs {budget_min:,.0f} — Rs {budget_max:,.0f}")
        st.metric("Preferred Rating", f"{profile['preferred_rating']:.1f}/5")
        st.caption(f"Based on {profile['total_searches']} searches")
        else:
        st.info("Start searching to build your style profile")

        st.markdown("---")
        st.markdown(f"### Saved Items: {db_stats['favorites']}")

        if st.button("View Saved Items", use_container_width=True):
        st.session_state.show_favorites = True
        if st.button("Clear All Favorites", use_container_width=True):
        FavoritesManager.clear_favorites()
        st.rerun()

        # ============================================================================
        # MAIN CONTENT - NAVIGATION & SEARCH
        # ============================================================================

        # Show favorites if requested
        if st.session_state.get('show_favorites', False):
        # Back button
        if st.button("← Back to Home"):
        st.session_state.show_favorites = False
        st.rerun()

        st.markdown("## Saved Items")
        st.divider()

        if favorites:
        for idx, fav in enumerate(favorites):
        col_image, col_info = st.columns([0.25, 0.75])

            with col_image:
        if 'image' in fav and fav['image']:
        img_url = fav['image']
                    # Add onerror handler to show placeholder if image fails to load
                    st.markdown(
                        f'<img src="{img_url}" style="width:100%; height:auto; object-fit:cover; border-radius:6px; min-height:250px; background:#ddd;" onerror="this.src=\'https://via.placeholder.com/200x250?text=No+Image\'"/>', unsafe_allow_html=True)
                        else:
                        st.markdown(
                        '<img src="https://via.placeholder.com/200x250?text=No+Image" style="width:100%; height:auto; border-radius:6px; min-height:250px;"/>', unsafe_allow_html=True)

                        with col_info:
                        st.markdown(f"**{fav['name'][:60]}**")
                        st.caption(f"Brand: {fav['seller'][:35]}")

                        badge_html = f'<div class="badge badge-price">Price: Rs {fav["price"]:,.0f}</div>'
                        badge_html += f'<div class="badge badge-rating">Rating: {fav["rating"]:.1f}/5</div>'

                        if fav.get('discount', 0) > 0:
                        badge_html += f'<div class="badge badge-discount">Discount: {fav["discount"]:.0f}%</div>'

                        st.markdown(badge_html, unsafe_allow_html=True)

                        if st.button("Remove", key=f"remove_{idx}", use_container_width=True):
                        FavoritesManager.remove_favorite(fav['name'])
                        st.rerun()

                        st.divider()
                            else:
        st.info("No saved items yet. Search and save products to your collection!")

                            else:
    # Main search and filter page
    search_query, min_price, max_price, min_rating, min_discount, occasion, gender, skin_tone, body_type= get_main_search_filters()

    # Search button
    if st.button("Search", use_container_width=True, key="main_search_btn"):
        st.session_state.search_executed= True
        st.session_state.last_search= {
            'query': search_query,
            'min_price': min_price,
            'max_price': max_price,
            'min_rating': min_rating,
            'min_discount': min_discount,
            'occasion': occasion,
            'gender': gender,
            'skin_tone': skin_tone,
            'body_type': body_type
        }

        # Show results if search was executed
        if st.session_state.get('search_executed', False):
        search_params = st.session_state.get('last_search', {})
        search_query = search_params.get('query', '')

        if not search_query:
        st.warning("Please enter a search term to find products")
        else:
        with st.spinner("Finding similar products..."):
                # Use a larger candidate pool first, then apply filters and show top results.
        results = recommender.recommend(
                   search_query,
                    top_n = 500,
                    preferred_gender = search_params.get('gender', 'All')
                )

                    if results is None:
                display_no_results()
                    else:
                    # Filter out disliked products
                disliked = FavoritesManager.get_disliked_products()
                    results= results[~results['name'].isin(disliked)]

                    # Apply filters
                    results= recommender.filter_by_price(
                       results, search_params['min_price'], search_params['max_price'])
                        results = recommender.filter_by_rating(
                        results, search_params['min_rating'])
                        results = recommender.filter_by_discount(
                        results, search_params['min_discount'])
                        results = recommender.filter_by_gender(
                        results, search_params.get('gender', 'All'))
                        results = recommender.filter_by_occasion(
                        results, search_params.get('occasion', 'All'))
                        results = recommender.filter_by_skin_tone(
                        results, search_params.get('skin_tone', 'All'))
                        results = recommender.filter_by_body_type(
                        results, search_params.get('body_type', 'All'))
                        results = results.head(10).reset_index(drop=True)

                        if results.empty:
                        st.warning(
                           "No products match your filter criteria. Try adjusting the filters.")
                            else:
                            # Record search in history
                            SearchHistoryManager.add_search(
                            query = search_query,
                            avg_price = results['price'].mean(),
                            avg_rating = results['rating'].mean(),
                            result_count = len(results)
                        )

                            # Results header
                            st.markdown(f"### Found {len(results)} Products")

                            # Build filter summary
                            filter_summary = []
                            if search_params.get('occasion') != 'All':
                        filter_summary.append(
                               f"Occasion: {search_params.get('occasion')}")
                                if search_params.get('gender') != 'All':
                                filter_summary.append(
                                f"Gender: {search_params.get('gender')}")
                                if search_params.get('skin_tone') != 'All':
                                filter_summary.append(
                                f"Skin Tone: {search_params.get('skin_tone')}")
                                if search_params.get('body_type') != 'All':
                                filter_summary.append(
                                f"Body Type: {search_params.get('body_type')}")

                                if filter_summary:
                                st.caption(
                                f"Filters: {' • '.join(filter_summary)}")

                                def toggle_favorite(product_row):
                                """Toggle favorite status."""
                                if FavoritesManager.is_favorite(product_row['name']):
                                FavoritesManager.remove_favorite(
                                   product_row['name'])
                                    else:
                                    FavoritesManager.add_favorite(
                                    product_row.to_dict())

                                    # Find query product index for explanations
                                    query_idx = df[df['name'].str.contains(
                            search_query, case=False, na=False)].index[0]

                                        for idx, (_, row) in enumerate(results.iterrows()):
                            col_image, col_product, col_actions= st.columns(
                                [0.25, 0.55, 0.2])

                                # Display product image
                                with col_image:
                                if 'image' in row.index and pd.notna(row['image']):
                                img_url = row['image']
                                    # Add onerror handler to show placeholder if image fails to load
                                    st.markdown(
                                        f'<img src="{img_url}" style="width:100%; height:auto; object-fit:cover; border-radius:6px; min-height:250px; background:#ddd;" onerror="this.src=\'https://via.placeholder.com/200x250?text=No+Image\'"/>', unsafe_allow_html =True)
                                        else:
                                        st.markdown(
                                        '<img src="https://via.placeholder.com/200x250?text=No+Image" style="width:100%; height:auto; border-radius:6px; min-height:250px;"/>', unsafe_allow_html =True)

                                        with col_product:
                                        st.markdown(f"**{row['name'][:55]}**")
                                        st.caption(f"Brand: {row['seller'][:35]}")

                                        # Get recommendation reason
                                        candidate_idx = df[df['name']
                                                  == row['name']].index[0]
                                                   reason = recommender.get_recommendation_reason(
                                    query_idx, candidate_idx)
                                    st.caption(f"Matched: {reason}")

                                    badge_html = f'<div class="badge badge-price">Rs {row["price"]:,.0f}</div>'
                                    badge_html += f'<div class="badge badge-rating">{row["rating"]:.1f}/5</div>'

                                    if row['discount'] > 0:
                                    badge_html += f'<div class="badge badge-discount">{row["discount"]:.0f}% off</div>'

                                    st.markdown(badge_html, unsafe_allow_html=True)

                                    with col_actions:
                                    st.markdown("###")
                                    is_fav = FavoritesManager.is_favorite(
                                    row['name'])
                                    btn_label = "Save" if not is_fav else "Saved"

                                    if st.button(btn_label, key=f"fav_{idx}", help="Save to collection", use_container_width=True):
                                    toggle_favorite(row)

                                    # Like/Dislike feedback buttons
                                    if st.button("Like", key=f"like_{idx}", use_container_width=True):
                                    FavoritesManager.add_feedback(
                                       row['name'], 'like', search_query)
                                        st.toast("Feedback recorded")

                                        if st.button("Dislike", key=f"dislike_{idx}", use_container_width=True):
                                        FavoritesManager.add_feedback(
                                        row['name'], 'dislike', search_query)
                                        st.toast("Product filtered")

                                        st.divider()

                                            # Footer
                                            st.markdown("---")
                                            st.markdown("""
<div style="text-align: center; color: #999; padding: 2rem 0;">
    <p>Khojo v2.1 | Advanced Fashion Recommendation Engine</p>
</div>
""", unsafe_allow_html=True)
