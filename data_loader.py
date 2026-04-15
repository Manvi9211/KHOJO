"""
Data loading and preprocessing module for the fashion recommender system.
Handles CSV loading, data cleaning, and feature engineering.
"""

import pandas as pd
import os
from typing import Optional, Tuple


def _download_from_url(url: str, output_path: str = "temp_dataset.csv") -> str:
    """
    Download CSV from URL with multiple fallback strategies.
    Returns the local path to the downloaded file.
    """
    import urllib.request

    # Try standard urllib first with User-Agent
    try:
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            with open(output_path, 'wb') as out_file:
                out_file.write(response.read())

        file_size = os.path.getsize(output_path)
        if file_size > 0:
            return output_path
    except Exception as e:
        pass

    # Try gdown for Google Drive URLs
    if 'drive.google.com' in url:
        try:
            import gdown
            gdown.download(url, output_path, quiet=False)
            file_size = os.path.getsize(output_path)
            if file_size > 0:
                return output_path
        except Exception as e:
            pass

    raise Exception(
        f"Failed to download from {url}. "
        f"Ensure the file is publicly accessible and not deleted. "
        f"Try hosting on GitHub Releases, Kaggle, or a direct cloud storage link."
    )


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
            # For URL sources, only download Google Drive links.
            # Direct HTTP CSV links (like GitHub Releases) are streamed by pandas.
            csv_to_load = self.csv_path
            is_url = self.csv_path.startswith('http://') or self.csv_path.startswith('https://')
            if is_url and 'drive.google.com' in self.csv_path:
                csv_to_load = _download_from_url(self.csv_path)

            # Read only header first to resolve schema without loading the full file.
            header_df = pd.read_csv(csv_to_load, nrows=0)
            raw_columns = list(header_df.columns)
            normalized_columns = [str(col).strip().replace('\n', '').replace('\r', '') for col in raw_columns]

            if len(normalized_columns) < 3:
                raise ValueError(
                    f"CSV has too few columns ({len(normalized_columns)}). "
                    f"Columns: {normalized_columns}"
                )

            normalized_to_original = {
                normalized_columns[i]: raw_columns[i] for i in range(len(raw_columns))
            }

            def pick_column(candidates):
                for candidate in candidates:
                    if candidate in normalized_to_original:
                        return normalized_to_original[candidate]
                return None

            col_name = pick_column(['name', 'product_name', 'title'])
            col_price = pick_column(['price', 'discounted_price', 'final_price'])
            col_rating = pick_column(['rating', 'ratings'])
            col_seller = pick_column(['seller', 'brand'])
            col_discount = pick_column(['discount', 'discount_percent'])
            col_img = pick_column(['img', 'image', 'image_url'])
            col_purl = pick_column(['purl', 'product_url', 'url'])

            mandatory = {
                'name': col_name,
                'price': col_price,
                'rating': col_rating,
                'img': col_img,
            }
            missing_mandatory = [k for k, v in mandatory.items() if v is None]
            if missing_mandatory:
                raise ValueError(
                    f"Missing required columns: {missing_mandatory}. "
                    f"Available columns: {normalized_columns}"
                )

            selected_columns = [c for c in [col_name, col_price, col_rating, col_seller, col_discount, col_img, col_purl] if c is not None]

            # Load only needed rows/columns to keep memory and startup time low on Streamlit Cloud.
            row_limit = max(self.sample_size * 3, self.sample_size)
            self.df = pd.read_csv(
                csv_to_load,
                usecols=selected_columns,
                nrows=row_limit,
                on_bad_lines='skip'
            )

            if self.df.empty:
                raise ValueError(f"CSV file is empty: {self.csv_path}")

            # Normalize column names to handle stray whitespace/newlines in headers
            self.df.columns = [str(col).strip().replace(
                '\n', '').replace('\r', '') for col in self.df.columns]

            # Canonicalize column names used by the app.
            rename_map = {}
            if col_name:
                rename_map[str(col_name).strip()] = 'name'
            if col_price:
                rename_map[str(col_price).strip()] = 'price'
            if col_rating:
                rename_map[str(col_rating).strip()] = 'rating'
            if col_seller:
                rename_map[str(col_seller).strip()] = 'seller'
            if col_discount:
                rename_map[str(col_discount).strip()] = 'discount'
            if col_img:
                rename_map[str(col_img).strip()] = 'img'
            if col_purl:
                rename_map[str(col_purl).strip()] = 'purl'
            self.df = self.df.rename(columns=rename_map)

            if 'seller' not in self.df.columns:
                # Provide a safe fallback when seller/brand is unavailable
                self.df['seller'] = 'Unknown Brand'
            if 'discount' not in self.df.columns:
                self.df['discount'] = 0
            if 'purl' not in self.df.columns:
                self.df['purl'] = ''

            # Select relevant columns with image and product URL metadata
            required_cols = ['name', 'price',
                             'rating', 'seller', 'discount', 'img', 'purl']

            missing_cols = [col for col in required_cols if col not in self.df.columns]
            if missing_cols:
                raise ValueError(
                    f"Missing required columns: {missing_cols}. "
                    f"Available columns: {list(self.df.columns)}"
                )

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

            # Keep the final dataframe bounded for responsive app startup.
            if len(self.df) > self.sample_size:
                self.df = self.df.head(self.sample_size).reset_index(drop=True)

            # Create features column for TF-IDF and include URL slug cues when available
            self.df['features'] = (
                self.df['name'].astype(str) + " " +
                self.df['seller'].astype(str) + " " +
                self.df['purl'].fillna('').astype(str)
            )

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
