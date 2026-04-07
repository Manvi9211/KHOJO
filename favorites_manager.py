"""
Favorites management module using SQLite persistence.
Allows users to save and manage their favorite products with persistent storage.
"""

import sqlite3
import json
from typing import List, Dict, Optional


class FavoritesManager:
    """Manages user favorites using SQLite for persistent storage."""

    DB_PATH = "khojo_favorites.db"

    @staticmethod
    def _get_connection():
        """Get SQLite database connection."""
        return sqlite3.connect(FavoritesManager.DB_PATH)

    @staticmethod
    def _init_db() -> None:
        """Initialize database schema if it doesn't exist."""
        conn = FavoritesManager._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT UNIQUE NOT NULL,
                data TEXT NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                feedback_type TEXT NOT NULL,
                query TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    @staticmethod
    def initialize_session() -> None:
        """Initialize database on app startup."""
        FavoritesManager._init_db()

    @staticmethod
    def add_favorite(product: Dict) -> bool:
        """
        Add a product to favorites.

        Args:
            product: Dictionary containing product details

        Returns:
            True if added, False if already exists
        """
        FavoritesManager._init_db()

        try:
            conn = FavoritesManager._get_connection()
            cursor = conn.cursor()

            product_data = json.dumps(product)
            cursor.execute(
                'INSERT INTO favorites (product_name, data) VALUES (?, ?)',
                (product['name'], product_data)
            )

            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            # Product already exists
            return False
        except Exception as e:
            print(f"Error adding favorite: {e}")
            return False

    @staticmethod
    def remove_favorite(product_name: str) -> bool:
        """
        Remove a product from favorites.

        Args:
            product_name: Name of the product to remove

        Returns:
            True if removed, False if not found
        """
        FavoritesManager._init_db()

        try:
            conn = FavoritesManager._get_connection()
            cursor = conn.cursor()

            cursor.execute(
                'DELETE FROM favorites WHERE product_name = ?', (product_name,))

            conn.commit()
            deleted = cursor.rowcount > 0
            conn.close()
            return deleted
        except Exception as e:
            print(f"Error removing favorite: {e}")
            return False

    @staticmethod
    def is_favorite(product_name: str) -> bool:
        """
        Check if a product is in favorites.

        Args:
            product_name: Name of the product

        Returns:
            True if product is favorited, False otherwise
        """
        FavoritesManager._init_db()

        try:
            conn = FavoritesManager._get_connection()
            cursor = conn.cursor()

            cursor.execute(
                'SELECT 1 FROM favorites WHERE product_name = ?', (product_name,))
            exists = cursor.fetchone() is not None
            conn.close()
            return exists
        except Exception as e:
            print(f"Error checking favorite: {e}")
            return False

    @staticmethod
    def get_favorites() -> List[Dict]:
        """
        Get all favorites.

        Returns:
            List of favorite products
        """
        FavoritesManager._init_db()

        try:
            conn = FavoritesManager._get_connection()
            cursor = conn.cursor()

            cursor.execute('SELECT data FROM favorites ORDER BY added_at DESC')
            rows = cursor.fetchall()
            conn.close()

            return [json.loads(row[0]) for row in rows]
        except Exception as e:
            print(f"Error getting favorites: {e}")
            return []

    @staticmethod
    def clear_favorites() -> bool:
        """
        Clear all favorites.

        Returns:
            True if successful
        """
        FavoritesManager._init_db()

        try:
            conn = FavoritesManager._get_connection()
            cursor = conn.cursor()

            cursor.execute('DELETE FROM favorites')

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error clearing favorites: {e}")
            return False

    @staticmethod
    def add_feedback(product_name: str, feedback_type: str, query: Optional[str] = None) -> bool:
        """
        Add user feedback (like/dislike) for a product.

        Args:
            product_name: Name of the product
            feedback_type: 'like' or 'dislike'
            query: The search query that led to this recommendation

        Returns:
            True if successful
        """
        FavoritesManager._init_db()

        try:
            conn = FavoritesManager._get_connection()
            cursor = conn.cursor()

            cursor.execute(
                'INSERT INTO feedback (product_name, feedback_type, query) VALUES (?, ?, ?)',
                (product_name, feedback_type, query)
            )

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding feedback: {e}")
            return False

    @staticmethod
    def get_disliked_products() -> set:
        """
        Get all products that have been disliked.

        Returns:
            Set of disliked product names
        """
        FavoritesManager._init_db()

        try:
            conn = FavoritesManager._get_connection()
            cursor = conn.cursor()

            cursor.execute(
                'SELECT product_name FROM feedback WHERE feedback_type = ?', ('dislike',))
            rows = cursor.fetchall()
            conn.close()

            return set(row[0] for row in rows)
        except Exception as e:
            print(f"Error getting disliked products: {e}")
            return set()

    @staticmethod
    def get_liked_sellers() -> Dict[str, int]:
        """
        Get sellers with most likes (for boosting their ranking).

        Returns:
            Dictionary mapping seller names to like counts
        """
        FavoritesManager._init_db()

        try:
            conn = FavoritesManager._get_connection()
            cursor = conn.cursor()

            # Get favorites and count by seller
            cursor.execute('SELECT data FROM favorites')
            rows = cursor.fetchall()
            conn.close()

            seller_counts = {}
            for row in rows:
                product = json.loads(row[0])
                seller = product.get('seller', 'Unknown')
                seller_counts[seller] = seller_counts.get(seller, 0) + 1

            return seller_counts
        except Exception as e:
            print(f"Error getting liked sellers: {e}")
            return {}

    @staticmethod
    def get_database_stats() -> Dict:
        """
        Get statistics about favorites and feedback.

        Returns:
            Dictionary with stats
        """
        FavoritesManager._init_db()

        try:
            conn = FavoritesManager._get_connection()
            cursor = conn.cursor()

            cursor.execute('SELECT COUNT(*) FROM favorites')
            favorite_count = cursor.fetchone()[0]

            cursor.execute(
                'SELECT COUNT(*) FROM feedback WHERE feedback_type = ?', ('like',))
            like_count = cursor.fetchone()[0]

            cursor.execute(
                'SELECT COUNT(*) FROM feedback WHERE feedback_type = ?', ('dislike',))
            dislike_count = cursor.fetchone()[0]

            conn.close()

            return {
                'favorites': favorite_count,
                'likes': like_count,
                'dislikes': dislike_count
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {'favorites': 0, 'likes': 0, 'dislikes': 0}
