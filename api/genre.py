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

    response = requests.get(base_url, params=params)
    data = response.json()
    
    genres = []
    if response.status_code == 200 and "artist" in data and "tags" in data["artist"]:
        genres = [tag["name"] for tag in data["artist"]["tags"]["tag"]]
    else:
        return []
    
    return genres

def get_weighted_genres(artists):
    weighted_genres = {}
    number_of_artists = len(artists)
    for i in range(0, number_of_artists):
        genres = get_artist_genre(artists[i])
        weighting = number_of_artists - i
        for genre in genres:
            if genre in weighted_genres:
                weighted_genres[genre] = weighted_genres[genre] + weighting
            else:
                weighted_genres[genre] = weighting
    
    return weighted_genres

def get_weighted_genres_dummy(artists):
    return {"Thrash Metal": 3, "Death Metal": 2}
