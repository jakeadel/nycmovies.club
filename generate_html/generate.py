from collections import defaultdict
from datetime import datetime
from jinja2 import Environment, FileSystemLoader


def get_all_theaters(cursor):
    query = "SELECT name FROM theaters"
    rows = cursor.execute(query, ()).fetchall()
    rows = [x[0] for x in rows]
    return rows


def get_all_showtimes(cursor, table):
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
        ORDER BY s.showtime ASC
    """

    rows = cursor.execute(query, ()).fetchall()
    if len(rows) < 1:
        raise Exception("No rows found for the get_all_showtimes function", table)
    columns = [desc[0] for desc in cursor.description]

    results = [dict(zip(columns, row)) for row in rows]

    for result in results:
        result["calendar_offset"] = time_to_percent(result.get("showtime"))
    
    return results


def time_to_percent(time_str):
    # % between 10am and 1am (16 sections)
    date_obj = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    
    hour = date_obj.hour
    minutes = date_obj.minute

    total = 15 * 60 # minutes between 10am and 1am

    # Avoid divide by 0
    if hour == 10 and minutes == 0:
        return 0
    else:
        pct = round((((hour - 10) * 60) + minutes) / total, 5)

    print(f"{hour=}, {minutes=}, {pct*100=}")
    return pct * 100


def group_showtimes_by_theater(showtimes):
    from collections import defaultdict

    def default_theater_entry():
        return {
            "name": "",
            "link": "",
            "address": "",
            "showtimes": []
        }

    theaters = defaultdict(default_theater_entry)

    for row in showtimes:
        name = row["theater_name"]
        theaters[name]["name"] = name
        theaters[name]["link"] = row["theater_url"]
        theaters[name]["address"] = row["theater_address"]

        theaters[name]["showtimes"].append({
            "title": row["title"].replace('"', "'"),
            "id": row["movie_id"],
            "wiki_link": row["wiki_link"],
            "image": row["image"],
            "runtime": format_runtime(row["runtime"]),
            "directors": row["directors"],
            "time": row["showtime"],
            "display_time": format_date(row["showtime"]),
            "calendar_offset": row["calendar_offset"],
            "link": row["showtime_link"]
        })

    # Sort showtimes by time
    for theater in theaters.values():
        theater["showtimes"].sort(key=lambda s: s["time"])

    # Sort theaters alpbabetically by name (may change)
    return sorted(theaters.values(), key=lambda t: t["name"])


def group_movies_by_title(showtimes):
    def default_entry():
        return {
            "title": "",
            "id": None,
            "wiki_link": None,
            "image": None,
            "theaters": []
        }

    grouped = defaultdict(default_entry)

    for row in showtimes:
        title = row["title"]
        grouped[title]["title"] = title.replace('"', "'")
        grouped[title]["id"] = row["movie_id"]
        grouped[title]["wiki_link"] = row["wiki_link"]
        grouped[title]["image"] = row["image"]
        grouped[title]["directors"] = row["directors"]
        grouped[title]["runtime"] = format_runtime(row["runtime"])
        grouped[title]["theaters"].append({
            "name": row["theater_name"],
            "link": row["theater_url"],
            "showtimes": [
                {
                    "time": row["showtime"],
                    "display_time": format_date(row["showtime"]),
                    "link": row["showtime_link"],
                    "calendar_offset": row["calendar_offset"]
                }
            ]
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
    date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
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


def generate_html(movie_data, theaters, theater_showtimes, dest):
    env = Environment(loader=FileSystemLoader("generate_html/templates"))
    table_template = env.get_template("table.html.j2")
    calendar_template = env.get_template("calendar.html.j2")

    formatted_date = datetime.now().strftime("%A %B, %d %Y")

    # NOTE: index and index-<today> will just have the same code I think
    with open(f"{dest}/index.html", "w") as f:
        f.write(table_template.render(movies=movie_data, theaters=theaters, date=formatted_date))

    with open(f"{dest}/table.html", "w") as f:
        f.write(table_template.render(movies=movie_data, theaters=theaters, date=formatted_date))
    
    times = [
        ("10am", 0.0),
        ("11am", 6.67),
        ("12pm", 13.33),
        ("1pm", 20.0),
        ("2pm", 26.67),
        ("3pm", 33.33),
        ("4pm", 40.0),
        ("5pm", 46.67),
        ("6pm", 53.33),
        ("7pm", 60.0),
        ("8pm", 66.67),
        ("9pm", 73.33),
        ("10pm", 80.0),
        ("11pm", 86.67),
        ("12am", 93.33)
    ]

    with open(f"{dest}/calendar.html", "w") as f:
        f.write(
            calendar_template.render(
                movies=movie_data, 
                theaters=theater_showtimes, 
                date=formatted_date,
                times=times
            )
        )


def handle_generate(cursor, table, date, dest):
    theaters = get_all_theaters(cursor)
    all_showtimes = get_all_showtimes(cursor, table)
    grouped = group_movies_by_title(all_showtimes)
    theater_showtimes = group_showtimes_by_theater(all_showtimes)

    generate_html(grouped, theaters, theater_showtimes, dest)


if __name__ == "__main__":
    print(time_to_percent("2025-04-13 23:00:00"))
