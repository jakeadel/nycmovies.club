import requests
import urllib

API_KEY = "ce9479aae14850e060f7dbd13d0f032e"
MOVIEDB_BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE = "https://image.tmdb.org/t/p/w200"

WIKI_BASE_URL = "https://en.wikipedia.org/w/api.php"
WIKI_ARTICLE_BASE = "https://en.wikipedia.org/wiki/"

def get_poster(title):
    url = f"{MOVIEDB_BASE_URL}/search/movie?api_key={API_KEY}&query={title}"
    res = requests.get(url)
    res.raise_for_status()
    data = res.json()
    movie = data['results'][0]
    poster_path = movie.get('poster_path')
    poster_url = IMAGE_BASE + poster_path
    return poster_url


def get_wikipedia_link(title):
    config = {
        "action": "query",
        "list": "search",
        "srsearch": title,
        "format": "json"
    }

    try:
        res = requests.get(WIKI_BASE_URL, params=config)
        data = res.json()
        search_results = data.get("query", {}).get("search", [])
        if not search_results:
            return None

        # Use the title of the top search result
        page_title = search_results[0]["title"]
        page_url = WIKI_ARTICLE_BASE + urllib.parse.quote(page_title.replace(" ", "_"))

        return page_url
    except Exception as e:
        print(f"Error grabbing wikipedia link for {title}, error:", e)
