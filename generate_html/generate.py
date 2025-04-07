import sqlite3
from collections import defaultdict
import datetime
from jinja2 import Environment, FileSystemLoader

def get_showtimes_for_today(cursor, table, date, db_path="movies.db"):
    query = f"""
        SELECT
            s.title,
            s.showtime,
            s.link AS showtime_link,
            s.theater_id,
            t.name AS theater_name,
            t.site_url AS theater_url,
            t.address as theater_address,
            m.id AS movie_id,
            m.wiki_link,
            m.image,
            m.runtime,
            m.directors
        FROM {table} s
        JOIN theaters t ON s.theater_id = t.id
        LEFT JOIN movies m ON s.title = m.title
        WHERE date(s.showtime) = date(?)
        ORDER BY s.showtime ASC
    """

    rows = cursor.execute(query, (date,)).fetchall()
    if len(rows) < 1:
        raise Exception("No rows found for:", date, "in table:", table)
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
        grouped[title]["directors"] = row["directors"]
        grouped[title]["runtime"] = format_runtime(row["runtime"])
        grouped[title]["theaters"].append({
            "name": row["theater_name"],
            "link": row["theater_url"],
            "showtimes": [{"time": row["showtime"], "display_time": format_date(row["showtime"]), "link": row["showtime_link"]}]
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


def format_date(date_str):
    date = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    formatted_date = date.strftime("%I:%M%p").lower()
    if (formatted_date[0] == '0'):
        formatted_date = formatted_date[1:]
    return formatted_date


def format_runtime(minutes):
    if not minutes or minutes == '0':
        return '-'
    hours = int(minutes) // 60
    minutes = int(minutes) % 60
    return f"{hours:01}:{minutes:02}"


def generate_html(movie_data, showtimes):
    env = Environment(loader=FileSystemLoader("generate_html/templates"))
    template = env.get_template("index.html.j2")
    table_template = env.get_template("table.html.j2")
    print(movie_data[0])
    with open("src/index.html", "w") as f:
        f.write(template.render(movies=movie_data))
    
    with open("src/table.html", "w") as f:
        f.write(table_template.render(movies=movie_data))


def handle_generate(cursor, table, date):
    showtimes = get_showtimes_for_today(cursor, table, date)
    grouped = group_movies_by_title(showtimes)
    generate_html(grouped, showtimes)


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