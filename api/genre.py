import requests
import os
import logging 

api_key = os.environ["genres_api_key"]

def get_artist_genre(artist):
    base_url = "http://ws.audioscrobbler.com/2.0/"
    
    params = {
        "method": "artist.getInfo",
        "artist": artist,
        "api_key": api_key,
        "format": "json"
    }

    try:
        logging.error("Trying request to: " + base_url)
        raise Exception("My error")
        #logging.error("Params: " + str(params))
        #response = requests.get(base_url, params=params)
        #requests.get("http://www.google.com")
    except Exception as e:
        logging.error("Exception: " + str(e))
    # data = response.json()
    
    genres = []
    # if response.status_code == 200 and "artist" in data and "tags" in data["artist"]:
    #     genres = [tag["name"] for tag in data["artist"]["tags"]["tag"]]
    # else:
    #     return []
    
    return genres

def get_weighted_genres(artists):
    weighted_genres = {}
    for artist in artists:
        genres = get_artist_genre(artist)
        for genre in genres:
            if genre in weighted_genres:
                weighted_genres[genre] = weighted_genres[genre] + 1
            else:
                weighted_genres[genre] = 1
    
    # return weighted_genres
    return {"Thrash Metal": 1}