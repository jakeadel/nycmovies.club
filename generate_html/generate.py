import sqlite3
from collections import defaultdict
from jinja2 import Environment, FileSystemLoader

def get_showtimes_for_today(cursor, table, db_path="movies.db"):
    query = f"""
        SELECT
            s.name AS title,
            s.showtime,
            s.link AS showtime_link,
            s.theater_id,
            t.name AS theater_name,
            t.site_url AS theater_url,
            t.address as theater_address,
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
        title = row["title"]
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
    
    # Sort by showtime, earliest first
    return sorted(grouped.values(), key=lambda m: m["theaters"][0]["showtimes"][0]["time"])

conn = sqlite3.connect("./movies.db")
cursor = conn.cursor()
def generate_html(movie_data, showtimes):
    env = Environment(loader=FileSystemLoader("generate_html/templates"))
    template = env.get_template("index.html.j2")
    table_template = env.get_template("table.html.j2")

    with open("generate_html/output/index.html", "w") as f:
        f.write(template.render(movies=movie_data))
    
    with open("generate_html/output/table.html", "w") as f:
        f.write(table_template.render(movies=showtimes))


def handle_generate(cursor, table, database):
    showtimes = get_showtimes_for_today(cursor, table)
    grouped = group_movies_by_title(showtimes)
    generate_html(grouped, showtimes)


handle_generate(cursor, 'showtimes_3_24_2025', "./movies.db")

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

"""
Is this better than a simple spreadsheet?
Maybe a good screen would just be all movies in a table sorted by time.
Can be selected maybe.
"""