import sys
import sqlite3
from datetime import datetime
import time

from utils import get_poster, get_wikipedia_link
from crawlers import pull_all, parse_all


def create_daily_table(cursor, table):
    cursor.execute(f"DROP TABLE IF EXISTS {table}")
    cursor.execute(f"""
        CREATE TABLE {table} (
            id INTEGER PRIMARY KEY,
            theater_id INT NOT NULL,
            title TEXT NOT NULL,
            showtime DATETIME,
            link TEXT NOT NULL,
            status INTEGER,
            created DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)


def insert_showtimes(cursor, table, showtimes):
    cursor.executemany(f"""
        INSERT INTO {table} 
            (theater_id, name, showtime, link) 
        VALUES 
            (?, ?, ?, ?);
    """, showtimes)


def is_movie_initialized(cursor, title):
    sql = "SELECT title FROM movies WHERE title = ? LIMIT 1"
    cursor.execute(sql, (title,))
    res = cursor.fetchone()

    if res is not None:
        return True
    return False


def initialize_movie(cursor, title):
    try:
        # wiki_link = get_wikipedia_link(title)
        wiki_link = None
    except Exception as e:
        wiki_link = None
        print(f"Unable to fetch wiki link for: {title}")
        print(e)
    
    try:
        poster = get_poster(title)
    except Exception as e:
        poster = None
        print(f"Unable to fetch poster for: {title}")
        print(e)

    sql = "INSERT INTO movies (title, wiki_link, image) VALUES (?, ?, ?);"
    cursor.execute(sql, (title, wiki_link, poster,))


def handle_showtimes(cursor, showtimes_table, showtimes):
    seen = set()
    for showtime in showtimes:
        title = showtime[1]
        if title not in seen and not is_movie_initialized(cursor, title):
            seen.add(title)
            initialize_movie(cursor, title)
            time.sleep(0.1)
    
    insert_showtimes(cursor, showtimes_table, showtimes)


def handle_crawl():
    conn = sqlite3.connect("../movies.db")
    cursor = conn.cursor()
    date = datetime.now()
    table = f"showtimes_{date.month}_{date.day}_{date.year}"
    print(f"{table=}")
    create_daily_table(cursor, table)

    pull_all()
    showtimes = parse_all()
    handle_showtimes(cursor, table, showtimes)

    conn.commit()
    conn.close()


def handle_build():
    pass


if __name__ == "__main__":
    try:
        action = sys.argv[1]
    except IndexError:
        raise Exception("No action argument provided")

    if action == 'crawl':
        handle_crawl()
    elif action == 'build':
        handle_build()
    else:
        print("Invalid input")
