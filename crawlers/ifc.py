import os
import requests
from datetime import datetime
from bs4 import BeautifulSoup as bs

URL = "https://www.ifccenter.com/"
NAME = "ICF"
HTML_FILE_NAME = "ifc.html"
DB_THEATER_ID = 3


def pull_html():
    headers = {
        'User-Agent': 'nycmovies.club'
    }
    html = requests.get(URL, headers=headers)
    if not html:
        print(f"{html.status_code}")
        raise Exception(f"html blank from {NAME}")
    current_directory = os.getcwd()

    # Print the current working directory
    print("Current working directory:", current_directory)
    with open(f"crawlers/html/{HTML_FILE_NAME}", "w") as file:
        file.write(html.text)


def parse_html():
    html = None
    with open(f"crawlers/html/{HTML_FILE_NAME}", "r") as file:
        html = file.read()
    print(len(html))
    soup = bs(html, "html.parser")
    days = soup.find_all(class_="daily-schedule")
    current_year = datetime.now().year
    current_month = datetime.now().month
    showtimes = []
    for day in days[0:-1]:
        date = day.find('h3').text
        movies = [[movie.find('h3').text, movie.find('a')['href']] for movie in day.find_all(class_='details')]
        timeTags = [elem.find_all('a') for elem in day.find_all(class_='times')]
        times = []
        links = []
        for tag in timeTags:
            tempTimes = []
            for a in tag:
                tempTimes.append(a.text)
                links.append(a['href'])
            times.append(tempTimes)
        for [title, showings, link] in zip(movies, times, links):
            for showing in showings:
                date_str = f"{date} {current_year} {showing}".strip()
                dt = datetime.strptime(date_str, "%a %b %d %Y %I:%M %p")
                showtime_year = current_year
                if dt.month < current_month:
                    showtime_year += 1
                
                final_date = dt.replace(year=showtime_year)

                showtimes.append([
                    DB_THEATER_ID,
                    title[0], # index 1 is link to movie not showtime specific
                    final_date,
                    link
                ])

    return showtimes
