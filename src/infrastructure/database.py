import logging
import sqlite3
from typing import List, Optional, Tuple

from src.core.models import Article, Law


class LawRepository:
    def __init__(self, db_path: str = "welfare_laws_v3.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Laws table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS laws (
                    law_id TEXT PRIMARY KEY,
                    law_num TEXT,
                    law_full_name TEXT,
                    last_updated TIMESTAMP
                )
            """)
            # Articles table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    law_id TEXT,
                    article_number TEXT,
                    hierarchy TEXT,
                    content TEXT,
                    FOREIGN KEY (law_id) REFERENCES laws (law_id)
                )
            """)
            conn.commit()

    def save_law(self, law: Law):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO laws (law_id, law_num, law_full_name, last_updated)
                VALUES (?, ?, ?, ?)
            """,
                (law.law_id, law.law_num, law.law_full_name, law.last_updated),
            )
            conn.commit()

    def save_articles(self, articles: List[Article]):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # まずその法律の条文をクリアするかどうかは更新戦略によるが、
            # 今回はシンプルに追加（実際はDELETE -> INSERTが良い）
            if not articles:
                return

            law_id = articles[0].law_id
            cursor.execute("DELETE FROM articles WHERE law_id = ?", (law_id,))

            data = [
                (a.law_id, a.article_number, a.hierarchy, a.content) for a in articles
            ]
            cursor.executemany(
                """
                INSERT INTO articles (law_id, article_number, hierarchy, content)
                VALUES (?, ?, ?, ?)
            """,
                data,
            )
            conn.commit()

    def get_all_articles(self) -> List[tuple]:
        """テスト用: 全条文取得"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT law_id, article_number, content FROM articles LIMIT 5"
            )
            return cursor.fetchall()
