import requests
import sqlite3
from datetime import datetime

from metrograph import pull_html as metrograph_pull
from metrograph import parse_html as metrograph_parse
from quad_cinema import pull_html as quad_pull
from quad_cinema import parse_html as quad_parse

"""
    I think don't worry about conflicts? Probably just wipe the movie table everytime
    or create a new table daily
"""



def createDailyTable(cursor, table):
    cursor.execute(f"DROP TABLE IF EXISTS {table}")
    cursor.execute(f"""
        CREATE TABLE {table} (
            id INTEGER PRIMARY KEY,
            theater_id INT NOT NULL,
            name TEXT NOT NULL,
            showtime TEXT NOT NULL,
            link TEXT NOT NULL,
            status INTEGER,
            wikipedia_link TEXT,
            created DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)

def insertShowtimes(cursor, table, showtimes):
    cursor.executemany(f"""
        INSERT INTO {table} 
            (theater_id, name, showtime, link) 
        VALUES 
            (?, ?, ?, ?);
    """, showtimes)


def getWikipediaLink(title):
    url = "https://en.wikipedia.org/w/api.php"
    config = {
        "action": "query",
        "list": "search",
        "srsearch": title,
        "format": "json"
    }

    try:
        res = requests.get(url, params=config)
        data = res.json()
    except Exception as e:
        print(f"Error grabbing wikipedia link for {title}, error:", e)
    print("DATA", data)
    
    

# I don't know what the alternative is but this sucks
if __name__ == "__main__":
 
    conn = sqlite3.connect("movies.db")
    cursor = conn.cursor()
    showtimes = quad_parse()
    now = datetime.now()
    new_table = f"movies_{now.year}_{now.month}_{now.day}"
    createDailyTable(cursor, new_table)
    insertShowtimes(cursor, new_table, showtimes)
    conn.commit()
