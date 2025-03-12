import requests
from datetime import datetime
from bs4 import BeautifulSoup as bs


URL = "https://www.metrograph.com/film"
NAME = "Metrograph"
HTML_FILE_NAME = "metrograph.html"
DB_THEATER_ID = 1

def pull_html():
    html = requests.get(URL)
    print(html.text)
    if not html:
        print(f"{html.status_code}")
        raise Exception(f"html blank from {NAME}")
    with open(f"html/{HTML_FILE_NAME}", "w") as file:
        file.write(html.text)

def parse_html():
    html = None
    with open(f"html/{HTML_FILE_NAME}", "r") as file:
        html = file.read()
    print(len(html))
    soup = bs(html, "html.parser")
    titles = soup.find_all(class_='movie_title')
    showings = [x.find_all(class_='film_day') for x in soup.find_all(class_='showtimes')]


    links = []
    for title in titles:
        print(title)
        link = title.find("a")["href"]
        links.append(link)

    showtimes = []

    print(len(titles), len(showings), len(links))
    assert len(titles) == len(showings) == len(links)

    current_year = datetime.now().year
    current_month = datetime.now().month

    for [title, showing, link] in zip(titles, showings, links):
        for show in showing:
            date = datetime.strptime(show.text, "%A %B %d %I:%M%p")

            showtime_year = current_year
            if date.month < current_month:
                showtime_year += 1
            
            final_date = date.replace(year=showtime_year)

            showtimes.append([
                DB_THEATER_ID,
                title.text,
                final_date, 
                link
            ])

    print(f"{showtimes=}")

    return showtimes
