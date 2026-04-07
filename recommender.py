"""
Recommendation engine module using TF-IDF and cosine similarity.
Provides product recommendations based on product name searches.
"""

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import Optional, List


class RecommendationEngine:
    """Handles product recommendations using TF-IDF similarity."""

    def __init__(self, dataframe: pd.DataFrame):
        """
        Initialize the recommendation engine.

        Args:
            dataframe: DataFrame with product data and 'features' column
        """
        self.df = dataframe.copy()
        self.tfidf_vectorizer = TfidfVectorizer(
            stop_words='english', max_features=5000)
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(
            self.df['features'])

    def _hybrid_score(self, sim_score: float, candidate_price: float, query_price: float, weight: float = 0.3) -> float:
        """
        Calculate hybrid score combining TF-IDF similarity and price band similarity.

        Args:
            sim_score: TF-IDF cosine similarity (0-1)
            candidate_price: Price of candidate product
            query_price: Price of query product
            weight: Weight of price similarity (0-1)

        Returns:
            Hybrid score combining text and price signals
        """
        if query_price <= 0:
            return sim_score

        # Price similarity: products within ±20% are scored higher
        price_diff_pct = abs(candidate_price - query_price) / query_price
        price_sim = max(0, 1 - price_diff_pct)

        # Combine text and price signals
        return (1 - weight) * sim_score + weight * price_sim

    def recommend(self, product_name: str, top_n: int = 10) -> Optional[pd.DataFrame]:
        """
        Get product recommendations based on a search query using hybrid scoring.

        Args:
            product_name: Name of the product to search for
            top_n: Number of recommendations to return

        Returns:
            DataFrame with recommended products or None if not found
        """
        if not product_name.strip():
            return None

        # Find matching product (partial match)
        matches = self.df[self.df['name'].str.contains(
            product_name, case=False, na=False)]

        if matches.empty:
            return None

        # Get index of first match
        idx = matches.index[0]
        query_price = self.df.iloc[idx]['price']

        # Calculate TF-IDF similarity scores
        sim_scores = cosine_similarity(
            self.tfidf_matrix[idx], self.tfidf_matrix)[0]

        # Apply hybrid scoring (TF-IDF + price band)
        hybrid_scores = []
        for i, tfidf_score in enumerate(sim_scores):
            candidate_price = self.df.iloc[i]['price']
            h_score = self._hybrid_score(
                tfidf_score, candidate_price, query_price)
            hybrid_scores.append((i, h_score))

        # Sort by hybrid score
        hybrid_scores = sorted(hybrid_scores, key=lambda x: x[1], reverse=True)

        # Exclude the product itself and get top N
        hybrid_scores = hybrid_scores[1:top_n + 1]

        # Get product indices
        product_indices = [i[0] for i in hybrid_scores]

        # Return results sorted by rating
        result = self.df[['name', 'seller', 'price',
                          'rating', 'discount', 'image']].iloc[product_indices].copy()
        return result.sort_values(by='rating', ascending=False).reset_index(drop=True)

    def filter_by_price(self, dataframe: pd.DataFrame, min_price: float,
                        max_price: float) -> pd.DataFrame:
        """Filter products by price range."""
        return dataframe[(dataframe['price'] >= min_price) & (dataframe['price'] <= max_price)]

    def filter_by_rating(self, dataframe: pd.DataFrame, min_rating: float) -> pd.DataFrame:
        """Filter products by minimum rating."""
        return dataframe[dataframe['rating'] >= min_rating]

    def filter_by_discount(self, dataframe: pd.DataFrame, min_discount: float) -> pd.DataFrame:
        """Filter products by minimum discount."""
        return dataframe[dataframe['discount'] >= min_discount]

    def _infer_gender(self, product_name: str) -> str:
        """
        Infer gender from product name.

        Args:
            product_name: Name of the product

        Returns:
            'Men', 'Women', or 'Unisex'
        """
        name_lower = product_name.lower()

        # Check for women indicators (expanded list)
        women_keywords = ['women', 'ladies', 'womens', 'woman', 'girl', 'girls',
                          'dress', 'saree', 'kurti', 'kurta', 'dupatta', 'pallav',
                          'lehenga', 'suit set', 'ethnic wear', 'salwar', 'kameez',
                          'tops for women', 'shirts for women', 'tees for women',
                          'palazzo', 'sharara', 'gown', 'blouse', 'bra', 'harem']

        # Check for men indicators (expanded list)
        men_keywords = ['men', 'mens', 'male', 'boy', 'boys', 'shirt',
                        'dhoti', 'kurta for men', 'tshirts for men', 'shirts for men',
                        'trousers', 'pants for men', 'traditional wear', 'waistcoat',
                        'suit for men', 'jacket for men']

        women_count = sum(
            1 for keyword in women_keywords if keyword in name_lower)
        men_count = sum(1 for keyword in men_keywords if keyword in name_lower)

        if women_count > men_count:
            return 'Women'
        elif men_count > women_count:
            return 'Men'
        elif women_count > 0:
            return 'Women'
        elif men_count > 0:
            return 'Men'

        return 'Unisex'

    def _infer_occasion(self, product_name: str) -> str:
        """
        Infer occasion from product name.

        Args:
            product_name: Name of the product

        Returns:
            Occasion type (Casual, Formal, Party, Sports, Traditional, Other)
        """
        name_lower = product_name.lower()

        casual_keywords = ['t-shirt', 'tshirt', 'casual', 'jeans', 'shorts',
                           'joggers', 'lounge', 'basic tee', 'everyday', 'denim']
        formal_keywords = ['blazer', 'suit', 'formal', 'dress pants', 'tie',
                           'trouser', 'waistcoat', 'business', 'office', 'shirt']
        party_keywords = ['dress', 'gown', 'party', 'saree', 'lehenga', 'ethnic',
                          'occasion wear', 'evening', 'wedding', 'cocktail', 'bride']
        sports_keywords = ['track', 'jersey', 'sports', 'running', 'gym', 'athletic',
                           'activewear', 'workout', 'training', 'performance']
        traditional_keywords = ['saree', 'lehenga', 'kurta', 'kurti', 'ethnic',
                                'traditional', 'dhoti', 'dupatta', 'suit set', 'salwar']

        # Check traditional first (highest priority)
        for keyword in traditional_keywords:
            if keyword in name_lower:
                return 'Traditional'

        # Check party wear
        party_score = sum(
            1 for keyword in party_keywords if keyword in name_lower)
        if party_score >= 1 and 'casual' not in name_lower:
            return 'Party'

        # Check sports
        for keyword in sports_keywords:
            if keyword in name_lower:
                return 'Sports'

        # Check formal
        for keyword in formal_keywords:
            if keyword in name_lower:
                return 'Formal'

        # Check casual
        for keyword in casual_keywords:
            if keyword in name_lower:
                return 'Casual'

        return 'Casual'

    def filter_by_gender(self, dataframe: pd.DataFrame, gender: str) -> pd.DataFrame:
        """
        Filter products by gender (inferred from product name).

        Args:
            dataframe: Products dataframe
            gender: 'Men', 'Women', 'All', or 'Unisex'

        Returns:
            Filtered dataframe
        """
        if gender == 'All':
            return dataframe

        # Infer gender for each product
        inferred_genders = dataframe['name'].apply(self._infer_gender)

        if gender in ['Men', 'Women']:
            return dataframe[inferred_genders == gender]
        elif gender == 'Unisex':
            return dataframe[inferred_genders == 'Unisex']

        return dataframe

    def filter_by_occasion(self, dataframe: pd.DataFrame, occasion: str) -> pd.DataFrame:
        """
        Filter products by occasion (inferred from product name).

        Args:
            dataframe: Products dataframe
            occasion: Occasion type to filter by

        Returns:
            Filtered dataframe
        """
        if occasion == 'All':
            return dataframe

        # Infer occasion for each product
        inferred_occasions = dataframe['name'].apply(self._infer_occasion)

        return dataframe[inferred_occasions == occasion]

    def get_recommendation_reason(self, query_idx: int, candidate_idx: int) -> str:
        """
        Generate explanation for why a product was recommended.

        Args:
            query_idx: Index of the query product
            candidate_idx: Index of the candidate product

        Returns:
            Human-readable explanation string
        """
        query_row = self.df.iloc[query_idx]
        candidate_row = self.df.iloc[candidate_idx]

        reasons = []

        # Price similarity signal
        price_diff = abs(candidate_row['price'] - query_row['price'])
        if price_diff < 500:
            reasons.append("Similar price")
        elif candidate_row['price'] < query_row['price']:
            reasons.append("Budget-friendly")
        else:
            reasons.append("Premium option")

        # Rating signal
        if candidate_row['rating'] >= 4.5:
            reasons.append("Highly rated")
        elif candidate_row['rating'] >= 4.0:
            reasons.append("Good rating")

        # Discount signal
        if candidate_row['discount'] > 30:
            reasons.append(f"{candidate_row['discount']:.0f}% discount")

        # Brand signal
        if candidate_row['seller'] == query_row['seller']:
            reasons.append("Same brand")

        if not reasons:
            reasons.append("Style match")

        return " | ".join(reasons)
