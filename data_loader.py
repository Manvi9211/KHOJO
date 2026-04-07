"""
Data loading and preprocessing module for the fashion recommender system.
Handles CSV loading, data cleaning, and feature engineering.
"""

import pandas as pd
from typing import Optional, Tuple


class DataLoader:
    """Manages loading and preprocessing of fashion product data."""

    def __init__(self, csv_path: str = "myntra.csv", sample_size: int = 10000):
        """
        Initialize the DataLoader.

        Args:
            csv_path: Path to the CSV file
            sample_size: Number of samples to use (for performance)
        """
        self.csv_path = csv_path
        self.sample_size = sample_size
        self.df = None
        self.load_and_process()

    def load_and_process(self) -> None:
        """Load CSV and apply all preprocessing steps."""
        try:
            # Load dataset
            self.df = pd.read_csv(self.csv_path)

            # Select relevant columns with image
            required_cols = ['name', 'price',
                             'rating', 'seller', 'discount', 'img']
            self.df = self.df[required_cols].copy()

            # Rename 'img' to 'image' for consistency
            self.df = self.df.rename(columns={'img': 'image'})

            # Convert data types
            self.df['price'] = pd.to_numeric(self.df['price'], errors='coerce')
            self.df['rating'] = pd.to_numeric(
                self.df['rating'], errors='coerce')
            self.df['discount'] = pd.to_numeric(
                self.df['discount'], errors='coerce')

            # Remove missing values (keep rows with missing images)
            numeric_cols = ['price', 'rating', 'discount']
            self.df = self.df.dropna(
                subset=numeric_cols).reset_index(drop=True)

            # Clean up image URLs - extract first image from semicolon-separated list
            placeholder = "https://via.placeholder.com/200x250?text=No+Image"

            def extract_first_image(img_str):
                if pd.isna(img_str) or not img_str:
                    return placeholder

                img_str = str(img_str).strip()

                # Handle invalid entries
                if not img_str or img_str == '-' or img_str == 'nan':
                    return placeholder

                # Split by semicolon and get first URL
                urls = img_str.split(';')
                first_url = urls[0].strip()

                # Validate URL
                if not first_url or first_url == '-' or len(first_url) < 10:
                    return placeholder

                # Ensure HTTPS
                if first_url.startswith('http://'):
                    first_url = first_url.replace('http://', 'https://', 1)
                elif not first_url.startswith('https://'):
                    return placeholder

                return first_url

            self.df['image'] = self.df['image'].apply(extract_first_image)

            # Sample for performance
            if len(self.df) > self.sample_size:
                self.df = self.df.sample(
                    self.sample_size, random_state=42).reset_index(drop=True)

            # Create features column for TF-IDF
            self.df['features'] = self.df['name'] + " " + self.df['seller']

        except FileNotFoundError:
            raise FileNotFoundError(f"Dataset file not found: {self.csv_path}")
        except Exception as e:
            raise Exception(f"Error loading data: {str(e)}")

    def get_dataframe(self) -> pd.DataFrame:
        """Return the processed dataframe."""
        return self.df

    def get_stats(self) -> dict:
        """Get dataset statistics."""
        return {
            'total_products': len(self.df),
            'avg_price': self.df['price'].mean(),
            'avg_rating': self.df['rating'].mean(),
            'price_range': (self.df['price'].min(), self.df['price'].max()),
            'rating_range': (self.df['rating'].min(), self.df['rating'].max())
        }
