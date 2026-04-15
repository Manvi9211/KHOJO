"""
Recommendation engine module using TF-IDF and cosine similarity.
Provides product recommendations based on product name searches.
"""

import pandas as pd
import re
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

    def _category_rules(self) -> dict:
        """Canonical product categories with positive and conflicting terms."""
        return {
            'shirt': {
                'include': ['shirt', 'shirts', 'tshirt', 't-shirt', 'tee', 'tees', 'top', 'tops'],
                'conflict': ['bra', 'bralette', 'lingerie', 'innerwear', 'panty', 'briefs']
            },
            'bra': {
                'include': ['bra', 'bralette', 'sports bra', 'lingerie', 'innerwear'],
                'conflict': ['shirt', 'tshirt', 't-shirt', 'tee', 'kurta', 'dress', 'jeans']
            },
            'jeans': {
                'include': ['jean', 'jeans', 'denim'],
                'conflict': ['bra', 'bralette', 'lingerie']
            },
            'kurti': {
                'include': ['kurti', 'kurtis', 'kurta', 'kurtas'],
                'conflict': ['bra', 'bralette', 'lingerie']
            },
            'dress': {
                'include': ['dress', 'dresses', 'gown'],
                'conflict': ['bra', 'bralette', 'lingerie']
            },
            'shoes': {
                'include': ['shoe', 'shoes', 'sneaker', 'sneakers', 'footwear'],
                'conflict': ['bra', 'bralette', 'lingerie']
            },
        }

    def _tokenize_query(self, query: str) -> List[str]:
        """Extract meaningful tokens from a user query."""
        cleaned = re.sub(r"[^a-z0-9\s-]", " ", str(query).lower())
        stop_words = {
            'for', 'with', 'and', 'the', 'from', 'under', 'over',
            'best', 'buy', 'new', 'latest', 'style', 'fashion'
        }
        return [t for t in cleaned.split() if len(t) >= 3 and t not in stop_words]

    def _query_token_variants(self, token: str) -> List[str]:
        """Return lexical variants used for strict intent matching."""
        variants_map = {
            'shirt': ['shirt', 'shirts', 'tshirt', 't-shirt', 'tee', 'tees'],
            'tshirt': ['tshirt', 't-shirt', 'tee', 'tees', 'shirt', 'shirts'],
            't-shirt': ['t-shirt', 'tshirt', 'tee', 'tees', 'shirt', 'shirts'],
            'jean': ['jean', 'jeans', 'denim'],
            'jeans': ['jean', 'jeans', 'denim'],
            'bra': ['bra', 'bralette', 'sports bra'],
            'kurta': ['kurta', 'kurtas'],
            'kurti': ['kurti', 'kurti set', 'kurtis'],
            'dress': ['dress', 'dresses', 'gown'],
            'shoe': ['shoe', 'shoes', 'sneaker', 'sneakers'],
        }
        return variants_map.get(token, [token])

    def _query_categories(self, query: str) -> List[str]:
        """Detect which canonical categories are explicitly requested in the query."""
        text = str(query).lower()
        categories = []
        for category, rules in self._category_rules().items():
            if any(self._contains_phrase(text, term) for term in rules['include']):
                categories.append(category)
        return categories

    def _intent_confidence(self, row: pd.Series, query: str) -> float:
        """Score row relevance to query intent on a 0-1 scale."""
        tokens = self._tokenize_query(query)
        text = self._row_text_for_inference(row)

        if not tokens:
            return 1.0

        # Token-level confidence
        matched_tokens = 0
        for token in tokens:
            variants = self._query_token_variants(token)
            token_match = any(
                self._contains_phrase(text, v) or (
                    v.replace('-', '') in text.replace('-', ''))
                for v in variants
            )
            if token_match:
                matched_tokens += 1

        token_confidence = matched_tokens / max(len(tokens), 1)

        # Category-level confidence for common fashion classes
        query_categories = self._query_categories(query)
        if not query_categories:
            return token_confidence

        rules = self._category_rules()
        positive_match = False
        conflict_hit = False

        for cat in query_categories:
            cat_rules = rules.get(cat, {})
            includes = cat_rules.get('include', [])
            conflicts = cat_rules.get('conflict', [])

            if any(self._contains_phrase(text, term) for term in includes):
                positive_match = True
            if any(self._contains_phrase(text, term) for term in conflicts):
                conflict_hit = True

        if conflict_hit and not positive_match:
            return 0.0

        category_confidence = 1.0 if positive_match else 0.0

        # Blend token and category signals, weighting category higher for precision.
        return (0.35 * token_confidence) + (0.65 * category_confidence)

    def _matches_query_intent(self, row: pd.Series, query: str) -> bool:
        """Use confidence threshold to keep intent-aligned results."""
        return self._intent_confidence(row, query) >= 0.55

    def recommend(self, product_name: str, top_n: int = 10, preferred_gender: str = 'All') -> Optional[pd.DataFrame]:
        """
        Get product recommendations based on a search query using hybrid scoring.

        Args:
            product_name: Name of the product to search for
            top_n: Number of recommendations to return
            preferred_gender: Preferred gender for selecting the query anchor

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

        # Choose a query anchor. If gender is selected, prefer a seed from that gender.
        idx = matches.index[0]
        if preferred_gender in ['Men', 'Women', 'Unisex']:
            inferred = matches.apply(
                lambda row: self._infer_gender(self._row_text_for_inference(row)), axis=1
            )
            gender_matches = matches[inferred == preferred_gender]
            if not gender_matches.empty:
                idx = gender_matches.index[0]

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
        selected_cols = ['name', 'seller',
                         'price', 'rating', 'discount', 'image']
        if 'purl' in self.df.columns:
            selected_cols.append('purl')

        result = self.df[selected_cols].iloc[product_indices].copy()

        # Keep recommendations aligned with the user's search intent using confidence.
        result = result.copy()
        result['intent_confidence'] = result.apply(
            lambda row: self._intent_confidence(row, product_name), axis=1
        )
        intent_filtered = result[result['intent_confidence'] >= 0.55]

        if intent_filtered.empty:
            # Fallback: keep strongest intent matches if strict threshold removes all.
            result = result.sort_values(
                by='intent_confidence', ascending=False).head(top_n)
        else:
            result = intent_filtered

        result = result.drop(columns=['intent_confidence'], errors='ignore')

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

    def _contains_phrase(self, text: str, phrase: str) -> bool:
        """Match a keyword/phrase using word boundaries to reduce false positives."""
        parts = phrase.strip().split()
        if not parts:
            return False
        pattern = r"\b" + r"\s+".join(re.escape(part)
                                      for part in parts) + r"\b"
        return re.search(pattern, text) is not None

    def _infer_gender(self, product_text: str) -> str:
        """
        Infer gender from product name.

        Args:
            product_text: Combined product text (name/url)

        Returns:
            'Men', 'Women', or 'Unisex'
        """
        text = product_text.lower()

        # Check for women indicators (expanded list)
        women_keywords = ['women', 'ladies', 'womens', 'woman', 'girl', 'girls',
                          'dress', 'saree', 'kurti', 'kurta', 'dupatta', 'pallav',
                          'lehenga', 'suit set', 'ethnic wear', 'salwar', 'kameez',
                          'tops for women', 'shirts for women', 'shirt for women', 'women shirt', 'women shirts', 'tees for women',
                          'palazzo', 'sharara', 'gown', 'blouse', 'bra', 'harem']

        # Check for men indicators (expanded list)
        men_keywords = ['men', 'mens', 'male', 'boy', 'boys',
                        'dhoti', 'kurta for men', 'tshirts for men', 'shirts for men',
                        'shirt for men', 'men shirt', 'men shirts',
                        'trousers', 'pants for men', 'traditional wear', 'waistcoat',
                        'suit for men', 'jacket for men']

        women_count = sum(
            1 for keyword in women_keywords if self._contains_phrase(text, keyword))
        men_count = sum(
            1 for keyword in men_keywords if self._contains_phrase(text, keyword))

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
        inferred_genders = dataframe.apply(
            lambda row: self._infer_gender(self._row_text_for_inference(row)), axis=1
        )

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

    def _row_text_for_inference(self, row: pd.Series) -> str:
        """Build text context for rule-based inference from available fields."""
        name = str(row.get('name', ''))
        purl = str(row.get('purl', ''))
        return f"{name} {purl}".lower()

    def _infer_skin_tone(self, product_text: str) -> str:
        """
        Infer skin tone suitability from color cues in product name.

        Args:
            product_text: Combined product text (name/url)

        Returns:
            'Warm', 'Cool', 'Neutral', or 'Deep'
        """
        text = product_text.lower()

        warm_keywords = ['mustard', 'olive', 'rust', 'maroon', 'beige', 'camel',
                         'gold', 'peach', 'coral', 'cream', 'orange', 'tan', 'ochre']
        cool_keywords = ['blue', 'navy', 'lavender', 'purple', 'teal', 'mint',
                         'grey', 'silver', 'violet', 'aqua', 'lilac']
        neutral_keywords = ['black', 'white', 'brown', 'taupe',
                            'charcoal', 'khaki', 'ivory', 'nude', 'grey melange']
        deep_keywords = ['emerald', 'burgundy', 'wine', 'royal blue',
                         'fuchsia', 'plum', 'cobalt', 'crimson', 'bottle green']

        warm_score = sum(
            1 for keyword in warm_keywords if keyword in text)
        cool_score = sum(
            1 for keyword in cool_keywords if keyword in text)
        neutral_score = sum(
            1 for keyword in neutral_keywords if keyword in text)
        deep_score = sum(
            1 for keyword in deep_keywords if keyword in text)

        scores = {
            'Warm': warm_score,
            'Cool': cool_score,
            'Neutral': neutral_score,
            'Deep': deep_score,
        }

        best_match = max(scores, key=scores.get)
        if scores[best_match] == 0:
            return 'Neutral'
        return best_match

    def _infer_body_type(self, product_text: str) -> str:
        """
        Infer body type suitability from fit and silhouette keywords.

        Args:
            product_text: Combined product text (name/url)

        Returns:
            'Athletic', 'Slim', 'Curvy', 'Plus Size', 'Petite', or 'Regular'
        """
        text = product_text.lower()

        athletic_keywords = ['athletic', 'sport', 'running', 'training', 'active',
                             'performance', 'stretch fit', 'gym', 'workout', 'compression']
        slim_keywords = ['slim fit', 'skinny', 'tapered', 'tailored', 'fitted']
        curvy_keywords = ['a-line', 'flare', 'wrap',
                          'peplum', 'fit and flare', 'empire', 'bootcut']
        plus_size_keywords = ['plus size', 'xxl',
                              '3xl', '4xl', 'curve', 'curvy fit', 'extended size']
        petite_keywords = ['petite', 'cropped', 'short length', 'ankle length']
        regular_keywords = ['regular fit', 'relaxed fit',
                            'oversized', 'straight fit', 'straight']

        if any(keyword in text for keyword in plus_size_keywords):
            return 'Plus Size'
        if any(keyword in text for keyword in petite_keywords):
            return 'Petite'
        if any(keyword in text for keyword in athletic_keywords):
            return 'Athletic'
        if any(keyword in text for keyword in curvy_keywords):
            return 'Curvy'
        if any(keyword in text for keyword in slim_keywords):
            return 'Slim'
        if any(keyword in text for keyword in regular_keywords):
            return 'Regular'

        return 'Regular'

    def filter_by_skin_tone(self, dataframe: pd.DataFrame, skin_tone: str) -> pd.DataFrame:
        """
        Filter products by inferred skin tone compatibility.

        Args:
            dataframe: Products dataframe
            skin_tone: 'Warm', 'Cool', 'Neutral', 'Deep', or 'All'

        Returns:
            Filtered dataframe
        """
        if skin_tone == 'All':
            return dataframe

        inferred_skin_tones = dataframe.apply(
            lambda row: self._infer_skin_tone(self._row_text_for_inference(row)), axis=1
        )
        return dataframe[inferred_skin_tones == skin_tone]

    def filter_by_body_type(self, dataframe: pd.DataFrame, body_type: str) -> pd.DataFrame:
        """
        Filter products by inferred body type fit.

        Args:
            dataframe: Products dataframe
            body_type: 'Athletic', 'Slim', 'Curvy', 'Plus Size', 'Petite', 'Regular', or 'All'

        Returns:
            Filtered dataframe
        """
        if body_type == 'All':
            return dataframe

        inferred_body_types = dataframe.apply(
            lambda row: self._infer_body_type(self._row_text_for_inference(row)), axis=1
        )
        return dataframe[inferred_body_types == body_type]

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
