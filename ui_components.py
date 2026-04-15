"""
UI components and styling for the fashion recommender system.
Provides reusable Streamlit components with professional styling.
"""

import streamlit as st
import pandas as pd
from typing import Tuple


def apply_custom_styling() -> None:
    """Apply custom CSS styling to the Streamlit app."""
    st.markdown("""
    <style>
        /* Main container */
        .main {
            padding-top: 2rem;
        }
        
        /* Headers */
        h1, h2, h3 {
            color: #1f77b4;
            font-weight: 600;
        }
        
        /* Product cards */
        .product-card {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            background: #f9f9f9;
            transition: box-shadow 0.3s ease;
        }
        
        .product-card:hover {
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }
        
        /* Buttons */
        .stButton>button {
            border-radius: 6px;
            font-weight: 600;
            padding: 0.6rem 1.5rem;
            transition: all 0.3s ease;
        }
        
        /* Metric boxes */
        .metric-box {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 8px;
            text-align: center;
        }
        
        /* Badges */
        .badge {
            display: inline-block;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            margin-right: 0.5rem;
        }
        
        .badge-price {
            background: #d4e157;
            color: #33691e;
        }
        
        .badge-rating {
            background: #ffca28;
            color: #f57f17;
        }
        
        .badge-discount {
            background: #ef5350;
            color: white;
        }
    </style>
    """, unsafe_allow_html=True)


def display_product_card(row: pd.Series, index: int) -> None:
    """
    Display a single product as a professional card.

    Args:
        row: Product data (Series)
        index: Index for unique key
    """
    st.markdown(f"**{row['name'][:60]}**")
    st.caption(f"Brand: {row['seller'][:35]}")

    badge_html = f'<div class="badge badge-price">Price: Rs {row["price"]:,.0f}</div>'
    badge_html += f'<div class="badge badge-rating">Rating: {row["rating"]:.1f}/5</div>'

    if row['discount'] > 0:
        badge_html += f'<div class="badge badge-discount">Discount: {row["discount"]:.0f}%</div>'

    st.markdown(badge_html, unsafe_allow_html=True)
    st.divider()


def display_stats_boxes(stats: dict) -> None:
    """Display dataset statistics in info boxes."""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Products", f"{stats['total_products']:,}")

    with col2:
        st.metric("Average Price", f"Rs {stats['avg_price']:,.0f}")

    with col3:
        st.metric("Average Rating", f"{stats['avg_rating']:.2f}")

    with col4:
        st.metric(
            "Price Range", f"Rs {stats['price_range'][0]:,.0f} - Rs {stats['price_range'][1]:,.0f}")


def get_main_search_filters() -> Tuple[str, float, float, float, float, str, str, str, str]:
    """
    Get filter values from main page with advanced options.

    Returns:
        Tuple of (search_query, min_price, max_price, min_rating, min_discount,
                  occasion, gender, skin_tone, body_type)
    """
    st.markdown("### Find Your Perfect Fashion")

    # Search bar
    search_query = st.text_input(
        "Search product:",
        placeholder="e.g., T-shirt, Jeans, Saree, Jacket",
        key="main_search"
    )

    st.markdown("---")

    # Advanced filters in columns
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Price & Ratings**")
        min_price, max_price = st.slider(
            "Price Range (Rs)",
            min_value=0,
            max_value=100000,
            value=(0, 50000),
            step=1000,
            key="price_slider"
        )

        min_rating = st.slider(
            "Minimum Rating",
            min_value=0.0,
            max_value=5.0,
            value=0.0,
            step=0.5,
            key="rating_slider"
        )

    with col2:
        st.markdown("**Fashion Filters**")
        gender = st.selectbox(
            "Gender",
            options=["All", "Men", "Women", "Unisex"],
            key="gender_select"
        )

        occasion = st.selectbox(
            "Occasion",
            options=["All", "Casual", "Formal",
                     "Party", "Sports", "Traditional"],
            key="occasion_select"
        )

        skin_tone = st.selectbox(
            "Skin Tone Friendly",
            options=["All", "Warm", "Cool", "Neutral", "Deep"],
            key="skin_tone_select"
        )

        body_type = st.selectbox(
            "Body Type",
            options=["All", "Athletic", "Slim", "Regular",
                     "Curvy", "Plus Size", "Petite"],
            key="body_type_select"
        )

    st.markdown("---")

    min_discount = st.slider(
        "Minimum Discount (%)",
        min_value=0,
        max_value=100,
        value=0,
        step=5,
        key="discount_slider"
    )

    return search_query, min_price, max_price, min_rating, min_discount, occasion, gender, skin_tone, body_type


def display_no_results() -> None:
    """Display a friendly message when no results are found."""
    st.info("No matching products found. Try a different search term.")
