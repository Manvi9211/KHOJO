"""
Khojo: Professional Fashion Product Recommender System
A Streamlit application for discovering similar fashion products using TF-IDF similarity.
"""

from search_history import SearchHistoryManager
from favorites_manager import FavoritesManager
from ui_components import (
    apply_custom_styling,
    display_product_card,
    display_stats_boxes,
    get_main_search_filters,
    display_no_results
)
from recommender import RecommendationEngine
from data_loader import DataLoader
from pathlib import Path
import pandas as pd
import streamlit as st
import os

"""
Khojo: Professional Fashion Product Recommender System
A Streamlit application for discovering similar fashion products using TF-IDF similarity.
"""


st.set_page_config(
    page_title="Khojo - Fashion Recommender",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_custom_styling()


def _normalize_dataset_url(url: str) -> str:
    """Convert Google Drive share links to direct-download URL."""
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
    """Load and cache the dataset."""
    try:
        dataset_candidates = [
            Path("myntra202305041052.csv"),
            Path("myntra.csv"),
            Path("data/myntra202305041052.csv"),
            Path("data/myntra.csv"),
        ]

        env_dataset_path = os.getenv("DATASET_PATH", "").strip()
        if env_dataset_path:
            dataset_candidates.insert(0, Path(env_dataset_path))

        csv_source = next((str(path)
                          for path in dataset_candidates if path.exists()), None)

        if csv_source is None:
            try:
                secret_dataset_path = str(
                    st.secrets.get("DATASET_PATH", "")).strip()
                if secret_dataset_path:
                    csv_source = secret_dataset_path
            except Exception:
                pass

        if csv_source is None:
            env_dataset_url = os.getenv("DATASET_URL", "").strip()
            if env_dataset_url:
                csv_source = _normalize_dataset_url(env_dataset_url)

        if csv_source is None:
            try:
                secret_dataset_url = str(
                    st.secrets.get("DATASET_URL", "")).strip()
                if secret_dataset_url:
                    csv_source = _normalize_dataset_url(secret_dataset_url)
            except Exception:
                pass

        if csv_source is None:
            error_msg = """
            **Dataset Not Found**
            
            Please configure a dataset by doing ONE of the following:
            
            1. **Local Development**: Place `myntra202305041052.csv` or `myntra.csv` in the project root.
            
            2. **Streamlit Cloud Deployment**:
               - Go to your app settings → Secrets
               - Add: `DATASET_URL = "https://your-csv-download-url"`
               - Example with Google Drive: 
                 `DATASET_URL = "https://drive.google.com/uc?export=download&id=YOUR_FILE_ID"`
            
            3. **Environment Variable**:
               - Set: `DATASET_URL` or `DATASET_PATH` in your system/deployment environment
            
            See `.streamlit/secrets.toml.example` for template setup.
            """
            st.error(error_msg)
            st.stop()

        loader = DataLoader(csv_path=csv_source, sample_size=10000)
        return loader.get_dataframe(), loader.get_stats()

    except Exception as e:
        st.error(f"Error loading dataset: {str(e)}")
        st.stop()


@st.cache_resource
def create_recommender(df):
    """Create and cache the recommendation engine."""
    return RecommendationEngine(df)


# ✅ FIXED: Proper placement (outside functions)
df, stats = load_data()

try:
    st.cache_resource.clear()
except:
    pass

recommender = create_recommender(df)

FavoritesManager.initialize_session()
SearchHistoryManager.initialize()

if 'show_favorites' not in st.session_state:
    st.session_state.show_favorites = False
if 'search_executed' not in st.session_state:
    st.session_state.search_executed = False
if 'last_search' not in st.session_state:
    st.session_state.last_search = {}


st.markdown("""
<div style="text-align: center; margin-bottom: 2rem;">
    <h1>Khojo</h1>
    <p style="color: #666; font-size: 1.1rem;">Discover Fashion Products Tailored to Your Style</p>
</div>
""", unsafe_allow_html=True)


# ---------------- SIDEBAR ----------------
with st.sidebar:
    favorites = FavoritesManager.get_favorites()
    db_stats = FavoritesManager.get_database_stats()
    profile = SearchHistoryManager.get_user_style_profile()

    st.markdown("### Your Style Profile")

    if profile['has_profile']:
        st.metric("Average Budget", f"Rs {profile['average_budget']:,.0f}")
        st.metric("Preferred Rating", f"{profile['preferred_rating']:.1f}/5")
    else:
        st.info("Start searching to build your style profile")

    st.markdown(f"### Saved Items: {db_stats['favorites']}")

    if st.button("View Saved Items"):
        st.session_state.show_favorites = True
    if st.button("Clear All Favorites"):
        FavoritesManager.clear_favorites()
        st.rerun()


# ---------------- FAVORITES ----------------
if st.session_state.get('show_favorites', False):
    if st.button("← Back"):
        st.session_state.show_favorites = False
        st.rerun()

    st.markdown("## Saved Items")

    if favorites:
        for idx, fav in enumerate(favorites):
            col_img, col_info = st.columns([1, 3])

            with col_img:
                image_url = fav.get(
                    'image') or "https://via.placeholder.com/210x280?text=No+Image"
                st.image(image_url, width=180)

            with col_info:
                st.write(f"**{fav['name']}**")
                st.write(f"Price: Rs {fav['price']}")
                if st.button("Remove", key=f"remove_{idx}"):
                    FavoritesManager.remove_favorite(fav['name'])
                    st.rerun()

            st.divider()
    else:
        st.info("No saved items yet")


# ---------------- SEARCH ----------------
else:
    search_query, min_price, max_price, min_rating, min_discount, occasion, gender, skin_tone, body_type = get_main_search_filters()

    if st.button("Search"):
        st.session_state.search_executed = True
        st.session_state.last_search = {
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

    if st.session_state.get('search_executed', False):
        params = st.session_state['last_search']

        if not params['query']:
            st.warning("Enter a search term")
        else:
            results = recommender.recommend(
                params['query'],
                top_n=30,
                preferred_gender=params.get('gender', 'All')
            )

            if results is None or results.empty:
                display_no_results()
            else:
                results = recommender.filter_by_price(
                    results,
                    params.get('min_price', 0),
                    params.get('max_price', 100000)
                )
                results = recommender.filter_by_rating(
                    results,
                    params.get('min_rating', 0.0)
                )
                results = recommender.filter_by_discount(
                    results,
                    params.get('min_discount', 0)
                )
                results = recommender.filter_by_gender(
                    results,
                    params.get('gender', 'All')
                )
                results = recommender.filter_by_occasion(
                    results,
                    params.get('occasion', 'All')
                )

                # Keep only top 10 after filters are applied.
                results = results.head(10)

                if results.empty:
                    st.warning(
                        "No products match your selected filters. Try widening your filters."
                    )
                    st.stop()

                st.markdown(f"### Found {len(results)} Products")

                for idx, (_, row) in enumerate(results.iterrows()):
                    col_img, col_info = st.columns([1, 3])

                    with col_img:
                        image_url = row.get(
                            'image') or "https://via.placeholder.com/210x280?text=No+Image"
                        st.image(image_url, width=180)

                    with col_info:
                        st.write(f"**{row['name']}**")
                        st.write(
                            f"Price: Rs {row['price']} | Rating: {row['rating']}")

                        if st.button("Save", key=f"fav_{idx}"):
                            FavoritesManager.add_favorite(row.to_dict())

                    st.divider()


st.markdown("---")
st.markdown("<center>Khojo v2.1</center>", unsafe_allow_html=True)
