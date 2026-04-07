"""
Search history and user style profile module.
Tracks user searches and infers style preferences.
"""

import sqlite3
import json
from typing import List, Dict, Optional
from datetime import datetime


class SearchHistoryManager:
    """Manages search history and builds user style profile."""

    DB_PATH = "khojo_favorites.db"

    @staticmethod
    def _get_connection():
        """Get SQLite database connection."""
        return sqlite3.connect(SearchHistoryManager.DB_PATH)

    @staticmethod
    def _init_db() -> None:
        """Initialize search history table if it doesn't exist."""
        conn = SearchHistoryManager._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                avg_price REAL,
                avg_rating REAL,
                result_count INTEGER,
                searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    @staticmethod
    def initialize() -> None:
        """Initialize search history on app startup."""
        SearchHistoryManager._init_db()

    @staticmethod
    def add_search(query: str, avg_price: float, avg_rating: float, result_count: int) -> bool:
        """
        Record a search in history.

        Args:
            query: Search query string
            avg_price: Average price of results
            avg_rating: Average rating of results
            result_count: Number of results returned

        Returns:
            True if successful
        """
        SearchHistoryManager._init_db()

        try:
            conn = SearchHistoryManager._get_connection()
            cursor = conn.cursor()

            cursor.execute(
                '''INSERT INTO search_history (query, avg_price, avg_rating, result_count) 
                   VALUES (?, ?, ?, ?)''',
                (query, avg_price, avg_rating, result_count)
            )

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding search: {e}")
            return False

    @staticmethod
    def get_search_history(limit: int = 10) -> List[Dict]:
        """
        Get recent search history.

        Args:
            limit: Maximum number of records to retrieve

        Returns:
            List of search history records
        """
        SearchHistoryManager._init_db()

        try:
            conn = SearchHistoryManager._get_connection()
            cursor = conn.cursor()

            cursor.execute(
                '''SELECT query, avg_price, avg_rating, result_count, searched_at 
                   FROM search_history 
                   ORDER BY searched_at DESC 
                   LIMIT ?''',
                (limit,)
            )
            rows = cursor.fetchall()
            conn.close()

            return [
                {
                    'query': row[0],
                    'avg_price': row[1],
                    'avg_rating': row[2],
                    'result_count': row[3],
                    'searched_at': row[4]
                }
                for row in rows
            ]
        except Exception as e:
            print(f"Error getting search history: {e}")
            return []

    @staticmethod
    def get_user_style_profile() -> Dict:
        """
        Infer user style profile from search history.

        Returns:
            Dictionary with budget, rating preference, and search trends
        """
        SearchHistoryManager._init_db()

        try:
            conn = SearchHistoryManager._get_connection()
            cursor = conn.cursor()

            cursor.execute(
                '''SELECT AVG(avg_price) as avg_budget, 
                          MIN(avg_price) as min_budget, 
                          MAX(avg_price) as max_budget,
                          AVG(avg_rating) as preferred_rating,
                          COUNT(*) as total_searches
                   FROM search_history'''
            )
            row = cursor.fetchone()

            # Get top search categories
            cursor.execute(
                '''SELECT query FROM search_history 
                   ORDER BY searched_at DESC 
                   LIMIT 5''',
            )
            recent_searches = [r[0] for r in cursor.fetchall()]

            conn.close()

            if row[0] is None:  # No searches yet
                return {
                    'budget_range': (0, 10000),
                    'preferred_rating': 0,
                    'total_searches': 0,
                    'recent_searches': [],
                    'has_profile': False
                }

            return {
                'average_budget': round(row[0], 2),
                'budget_range': (round(row[1], 2), round(row[2], 2)),
                'preferred_rating': round(row[3], 1),
                'total_searches': row[4],
                'recent_searches': recent_searches,
                'has_profile': row[4] > 2  # Profile exists after 3+ searches
            }
        except Exception as e:
            print(f"Error getting style profile: {e}")
            return {
                'budget_range': (0, 10000),
                'preferred_rating': 0,
                'total_searches': 0,
                'recent_searches': [],
                'has_profile': False
            }

    @staticmethod
    def clear_history() -> bool:
        """
        Clear all search history.

        Returns:
            True if successful
        """
        SearchHistoryManager._init_db()

        try:
            conn = SearchHistoryManager._get_connection()
            cursor = conn.cursor()

            cursor.execute('DELETE FROM search_history')

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error clearing history: {e}")
            return False
