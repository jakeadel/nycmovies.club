import sqlite3
from collections import defaultdict

def get_showtimes_for_today(cursor, table, db_path="movies.db"):
    query = f"""
        SELECT
            s.name AS movie_name,
            s.showtime,
            s.link AS showtime_link,
            s.theater_id,
            t.name AS theater_name,
            t.site_url AS theater_url,
            m.id AS movie_id,
            m.wiki_link,
            m.image
        FROM {table} s
        JOIN theaters t ON s.theater_id = t.id
        LEFT JOIN movies m ON s.name = m.title
        ORDER BY s.showtime ASC
    """

    rows = cursor.execute(query).fetchall()
    columns = [desc[0] for desc in cursor.description]
    print(rows[0])

    results = [dict(zip(columns, row)) for row in rows]
    return results


def group_movies_by_title(showtimes):
    grouped = defaultdict(lambda: {"title": "", "id": None, "wiki_link": None, "image": None, "theaters": []})

    for row in showtimes:
        title = row["movie_name"]
        grouped[title]["title"] = title
        grouped[title]["id"] = row["movie_id"]
        grouped[title]["wiki_link"] = row["wiki_link"]
        grouped[title]["image"] = row["image"]
        grouped[title]["theaters"].append({
            "name": row["theater_name"],
            "link": row["theater_url"],
            "showtimes": [{"time": row["showtime"], "link": row["showtime_link"]}]
        })

    # Group by theater
    for movie in grouped.values():
        theaters = defaultdict(lambda: {"name": "", "link": "", "showtimes": []})
        for theater in movie["theaters"]:
            key = theater["name"]
            theaters[key]["name"] = theater["name"]
            theaters[key]["link"] = theater["link"]
            theaters[key]["showtimes"].extend(theater["showtimes"])
        movie["theaters"] = list(theaters.values())
    
    print(grouped["Vive L'Amour"])

    # Sort by showtime, earliest first
    return sorted(grouped.values(), key=lambda m: m["theaters"][0]["showtimes"][0]["time"])

conn = sqlite3.connect("./movies.db")
cursor = conn.cursor()
def generate_html(cursor, table, database):
    showtimes = get_showtimes_for_today(cursor, table)
    grouped = group_movies_by_title(showtimes)
    print(grouped[0])
    # Then do the actual generation here

generate_html(cursor, 'showtimes_3_24_2025', "./movies.db")

"""
Need movies to look like:

{
    id: 1,
    title: The Matrix,
    general_link: ...,
    poster_link: ...,
    earliest_date: <timestamp>,
    theaters: [
        {
            name: Metrograph,
            showtimes: [
                {
                    time: ...,
                    link: ... 
                }
            ]
        }
    ]
}
"""
