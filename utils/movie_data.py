import os
import requests
import urllib

API_KEY = os.getenv("MOVIE_DB_API_KEY")
MOVIEDB_BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE = "https://image.tmdb.org/t/p/w200"
WIKI_BASE_URL = "https://en.wikipedia.org/w/api.php"
WIKI_ARTICLE_BASE = "https://en.wikipedia.org/wiki/"


def get_movie_details(title):
    # Search for the movie by title
    search_url = f"{MOVIEDB_BASE_URL}/search/movie?api_key={API_KEY}&query={title}"
    search_res = requests.get(search_url)
    search_res.raise_for_status()
    search_data = search_res.json()

    if not search_data['results']:
        return "No results found."

    # Get the first result and its movie ID
    movie = search_data['results'][0]
    movie_id = movie['id']

    # Request detailed movie information using the movie ID
    details_url = f"{MOVIEDB_BASE_URL}/movie/{movie_id}?api_key={API_KEY}"
    details_res = requests.get(details_url)
    details_res.raise_for_status()
    details_data = details_res.json()

    credits_url = f"{MOVIEDB_BASE_URL}/movie/{movie_id}/credits?api_key={API_KEY}"
    credits_res = requests.get(credits_url)
    credits_res.raise_for_status()
    credits_data = credits_res.json()
   # print("RESRESRSER", credits_res.json())

    # Extract needed details
    poster_path = details_data.get('poster_path')
    poster = IMAGE_BASE + poster_path if poster_path else "No poster available"
    runtime = details_data.get('runtime', 'Runtime not available')
    directors = ", ".join([crew['name'] for crew in credits_data.get('crew', []) if crew['job'] == 'Director'])
    print("ERERERRE", poster, runtime, directors)
    
    return {
        "poster": poster,
        "runtime": runtime,
        "directors": directors
    }

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
