import requests
from datetime import datetime
from bs4 import BeautifulSoup as bs

URL = "https://quadcinema.com/all/"
NAME = "Quad Cinema"
HTML_FILE_NAME = "quad_cinema.html"
DB_THEATER_ID = 2

def pull_html():
    headers = {
        'User-Agent': 'nycmovies.club'
    }
    html = requests.get(URL, headers=headers)
    if not html:
        print(f"{html.status_code}")
        raise Exception(f"html blank from {NAME}")
    with open(f"crawlers/html/{HTML_FILE_NAME}", "w") as file:
        file.write(html.text)


def parse_html():
    html = None
    with open(f"crawlers/html/{HTML_FILE_NAME}", "r") as file:
        html = file.read()
    print(len(html))
    soup = bs(html, "html.parser")
    days = soup.find_all(class_="now-single-day")
    showtimes = []
    current_year = datetime.now().year
    current_month = datetime.now().month
    for day in days:
        [month, date] = day.find(class_="trailing-rule-wrap").text.split(' ')[1:3]
        listings = day.find_all(class_="single-listing")
        for listing in listings:
            title = listing.find('h4').text
            times = listing.find_all("li")

            for time in times:
                link = time.find("a")["href"]
                time = time.text

                date_string = f"{date} {month} {time} {current_year}"
                try:
                    formatted_date = datetime.strptime(date_string, "%d %B %I.%M%p %Y")
                except ValueError:
                    print("Error parsing date for", title, "on", date_string)
                showtime_year = current_year
                if formatted_date.month < current_month:
                    showtime_year += 1
                final_date = formatted_date.replace(year=showtime_year)

                showtimes.append([
                    DB_THEATER_ID,
                    title,
                    final_date,
                    link
                ])
    
    return showtimes
