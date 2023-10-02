from genre import get_weighted_genres, get_weighted_genres_dummy
from repository import Repository

from datetime import datetime
from dateutil import parser
from dateutil.relativedelta import relativedelta

import json
import praw
import re
import os

class Post:
    def __init__(self, title, url, timestamp, is_self):
        self.title = title
        self.url = url
        self.timestamp = timestamp
        self.is_self = is_self

class Gig:
    def __init__(self, bands, venue, city, timestamps, url, genres):
        self.bands = bands
        self.venue = venue
        self.city = city
        self.timestamps = timestamps
        self.url = url
        self.genres = genres

    def as_serialisable(self):
        as_dict = self.__dict__
        as_dict["timestamps"] = [str(timestamp) for timestamp in as_dict["timestamps"]]
        return as_dict

class PostsApi:
    client_id = os.environ["gigs_api_client_id"]
    client_secret = os.environ["gigs_api_client_secret"]
    user_agent = "ScottishMetalGigs"
    subreddit_name = "MetalGigsScotland"

    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=self.client_id,
            client_secret=self.client_secret,
            user_agent=self.user_agent
        )

    def get_posts(self):
        subreddit = self.reddit.subreddit(self.subreddit_name)
        posts = subreddit.new(limit=1000)

        return [Post(post.title, post.url, datetime.fromtimestamp(post.created_utc), post.is_self) for post in posts]

def parse_dates_from_post_title(date):
    dates = []
    try:
        if "/" in date:
            segments = date.split("/")
            final_segment = segments[-1]
            final_date = parser.parse(final_segment)
            for segment in segments[:-1]:
                regex = r"(\d{1,2})(st|nd|rd|th)"
                match = re.match(regex, segment)
                if match:
                    day = match.group(1)
                    parsed_date = final_date.replace(day=int(day))
                else:
                    parsed_date = parser.parse(segment)
                dates.append(parsed_date)
            dates.append(final_date)
        else:
            dates.append(parser.parse(date))
    except ValueError:
        print("Could not parse the date: " + date)
        raise ValueError

    return dates

def is_post_recent(post):
    today = datetime.now()
    one_year_ago = today - relativedelta(years=1)
    return post.timestamp >= one_year_ago

def parse_post(post):
    pattern = r"(?P<bands>(?:.+)) - (?P<venue>.+)\((?P<city>.+)\) - (?P<date>.+)"
    match = re.match(pattern, post.title)

    if match:
        bands = [band.strip() for band in match.group("bands").split("/")]
        venue = match.group("venue").strip()
        city = match.group("city").strip()
        dates = parse_dates_from_post_title(match.group("date"))

        return Gig(bands, venue, city, dates, post.url, {})
    else:
        print("Pattern did not match: " + post.title)
        return None

def parse_posts(posts):
    gigs = []
    unparsed_posts = []
    for post in posts:
        try:
            gig = parse_post(post)
            gigs.append(gig)
        except ValueError:
            unparsed_posts.append(post)
    return gigs, unparsed_posts

def is_gig_in_past(gig):
    all_dates_in_past = True
    for timestamp in gig.timestamps:
        if timestamp.date() >= datetime.now().date():
            all_dates_in_past = False
    return all_dates_in_past

def are_gigs_equal(gig, gig_from_db):
    bands_equal = gig.bands == gig_from_db["bands"]
    venue_equal = gig.venue == gig_from_db["venue"]
    city_equal = gig.city == gig_from_db["city"]
    timestamps_equal = gig.timestamps == [parser.parse(timestamp) for timestamp in gig_from_db["timestamps"]]
    url_equal = gig.url == gig_from_db["url"]

    return bands_equal and venue_equal and city_equal and timestamps_equal and url_equal

def does_list_of_gigs_contain_gig(gigs, gig_to_find):
    list_contains_gig = False
    for gig in gigs:
        if are_gigs_equal(gig_to_find, gig):
            list_contains_gig = True
    return list_contains_gig

def gig_from_db_to_gig(gig_from_db):
    timestamps = [parser.parse(timestamp) for timestamp in gig_from_db["timestamps"]]
    return Gig(gig_from_db["bands"], gig_from_db["venue"], gig_from_db["city"], timestamps, gig_from_db["url"], gig_from_db["genres"])

def get_new_gigs():
    posts_api = PostsApi()
    posts = posts_api.get_posts()
    posts = [post for post in posts if is_post_recent(post) and not post.is_self]
    gigs, unparsed_posts = parse_posts(posts)
    gigs = [gig for gig in gigs if gig is not None and not is_gig_in_past(gig)]

    repository = Repository()
    existing_gigs = repository.get_gigs()

    new_gigs = [gig for gig in gigs if not does_list_of_gigs_contain_gig(existing_gigs, gig)]

    for gig in new_gigs:
        gig.genres = get_weighted_genres(gig.bands)

    repository.save_gigs(new_gigs)
    return json.dumps([gig.as_serialisable() for gig in new_gigs])

def get_existing_gigs():
    repository = Repository()
    existing_gigs = repository.get_gigs()
    return json.dumps([gig_from_db_to_gig(gig).as_serialisable() for gig in existing_gigs])