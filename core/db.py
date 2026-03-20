import aiosqlite
import os
import logging
from typing import Tuple, Optional, List, Dict
from datetime import datetime

DATABASE_FILE = "database/rpg.db"

TITLES = [
    (1, "الراوي المبتدئ"),
    (3, "صاحب الحكايا"),
    (5, "المحارب الناشئ"),
    (10, "حارس القصص"),
    (15, "صانع الأساطير"),
    (20, "سيد الروايات"),
    (30, "أسطورة الأبد")
]

async def init_db() -> None:
    """Initialize the database and ensure the players table exists."""
    if not os.path.exists("database"):
        os.makedirs("database")

    try:
        async with aiosqlite.connect(DATABASE_FILE) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS players (
                    user_id INTEGER PRIMARY KEY,
                    title TEXT,
                    stories_completed INTEGER DEFAULT 0,
                    joined_at TIMESTAMP
                )
            ''')
            await db.commit()
    except Exception as e:
        logging.error(f"Error initializing database: {e}")

async def get_player_profile(user_id: int) -> Tuple[Optional[str], int, Optional[str]]:
    """Get player title, stories completed, and join date."""
    try:
        async with aiosqlite.connect(DATABASE_FILE) as db:
            async with db.execute('SELECT title, stories_completed, joined_at FROM players WHERE user_id = ?', (user_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return row[0], row[1], row[2]
                return None, 0, None
    except Exception as e:
        logging.error(f"Error getting player profile for {user_id}: {e}")
        return None, 0, None

async def register_player(user_id: int) -> None:
    """Register a new player if they don't exist."""
    try:
         async with aiosqlite.connect(DATABASE_FILE) as db:
            await db.execute('''
                INSERT OR IGNORE INTO players (user_id, title, stories_completed, joined_at)
                VALUES (?, ?, ?, ?)
            ''', (user_id, "بدون لقب", 0, datetime.utcnow().isoformat()))
            await db.commit()
    except Exception as e:
        logging.error(f"Error registering player {user_id}: {e}")

async def increment_stories_completed(user_id: int) -> Optional[str]:
    """Increment stories completed and update title if a milestone is reached.
    Returns the new title if it was upgraded, otherwise None.
    """
    await register_player(user_id) # Ensure they exist

    try:
        async with aiosqlite.connect(DATABASE_FILE) as db:
            # Increment count
            await db.execute('UPDATE players SET stories_completed = stories_completed + 1 WHERE user_id = ?', (user_id,))

            # Fetch new count
            async with db.execute('SELECT stories_completed, title FROM players WHERE user_id = ?', (user_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    return None

                new_count, current_title = row

                # Determine new title
                new_title = None
                for milestone, title in reversed(TITLES):
                    if new_count >= milestone:
                        if current_title != title:
                            new_title = title
                        break

                # Update title if changed
                if new_title:
                    await db.execute('UPDATE players SET title = ? WHERE user_id = ?', (new_title, user_id))
                    await db.commit()
                    return new_title

                await db.commit()
                return None
    except Exception as e:
        logging.error(f"Error incrementing stories for {user_id}: {e}")
        return None

async def get_all_players() -> List[Dict]:
    """Return all players as a list of dictionaries for backup."""
    players = []
    try:
         async with aiosqlite.connect(DATABASE_FILE) as db:
            async with db.execute('SELECT user_id, title, stories_completed, joined_at FROM players') as cursor:
                 async for row in cursor:
                     players.append({
                         "user_id": row[0],
                         "title": row[1],
                         "stories_completed": row[2],
                         "joined_at": row[3]
                     })
    except Exception as e:
         logging.error(f"Error fetching all players: {e}")
    return players
