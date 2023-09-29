from genre import get_weighted_genres

from dataclasses import dataclass, asdict
from datetime import datetime
from dateutil import parser
from dateutil.relativedelta import relativedelta

import json
import praw
import re
import os

@dataclass
class Post:
    title: str
    url: str
    timestamp: datetime
    is_self: bool

@dataclass
class Gig:
    bands: list[str]
    venue: str
    city: str
    timestamps: list[datetime]
    url: str
    genres: dict[str, int]

client_id = os.environ["gigs_api_client_id"]
client_secret = os.environ["gigs_api_client_secret"]
user_agent = "ScottishMetalGigs"
subreddit_name = "MetalGigsScotland"

reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    user_agent=user_agent
)

def get_posts(subreddit_name):
    subreddit = reddit.subreddit(subreddit_name)
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

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

def get_gigs():
    posts = get_posts(subreddit_name)
    posts = [post for post in posts if is_post_recent(post) and not post.is_self]
    gigs, unparsed_posts = parse_posts(posts)
    gigs = [gig for gig in gigs if gig is not None and not is_gig_in_past(gig)]

    for gig in gigs:
        gig.genres = get_weighted_genres(gig.bands)

    json_data = json.dumps([asdict(gig) for gig in gigs], indent=4, default=json_serial)
    return json_data