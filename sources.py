"""Single source of truth for the 11 documents in the corpus.

Each entry has:
  - name   : short slug used for the output filename (documents/<name>.md)
  - title  : human-readable source label (stored as metadata, shown in answers)
  - url    : original URL (stored as metadata for attribution)
  - mode   : how the content is acquired —
        "scrape" : fetched live by scrape.py via requests
        "reddit" : fetched live via Reddit's .json endpoint (comment tree)
        "local"  : read from a manually-saved file in documents/raw/<file>
  - file   : (local mode only) the saved HTML filename in documents/raw/

Sites with bot walls / login (Apartments.com, ForRent, Yelp, Facebook) were
saved manually in the browser and are marked "local". Reddit, Kato, ochdatabase,
the official FAQ, and AmberStudent are attempted live; anything that blocks is
reported by scrape.py so it can be saved manually and flipped to "local".
"""

SOURCES = [
    {
        "name": "apartments_com",
        "title": "Apartments.com",
        "url": "https://www.apartments.com/university-view-college-park-md/jtb8837/",
        "mode": "local",
        "file": "ApartmentcomUView.html",
    },
    {
        "name": "forrent",
        "title": "ForRent",
        "url": "https://www.forrent.com/md/college-park/university-view/4tb8g3l",
        "mode": "local",
        "file": "ForRentUView.html",
    },
    {
        "name": "kato_housing",
        "title": "Kato Housing",
        "url": "https://katohousing.org/apartment/university-view",
        "mode": "local",
        "file": "KatoUView.html"
    },
    {
        "name": "ochdatabase",
        "title": "OCH Database (UMD)",
        "url": "https://ochdatabase.umd.edu/housing/property/university-view/2sbyc3c",
        "mode": "local",
        "file": "OHCDatabaseUView.html",
    },
    {
        "name": "reddit_uview_review",
        "title": "Reddit r/UMD — UView housing review",
        "url": "https://www.reddit.com/r/UMD/comments/1cg5mg6/uview_housing_review/",
        "mode": "local",
        "file": "HousingReviewUView.html",
    },
    {
        "name": "live_theview_faq",
        "title": "University View Official FAQ",
        "url": "https://live-theview.com/faqs/",
        "mode": "scrape",
    },
    {
        "name": "reddit_view_vs_varsity",
        "title": "Reddit r/UMD — View vs Varsity",
        "url": "https://www.reddit.com/r/UMD/comments/q5e4we/view_vs_varsity_any_advice/",
        "mode": "local",
        "file": "ViewVarsityUView.html",
    },
    {
        "name": "reddit_red_flags",
        "title": "Reddit r/UMD — red flags about new apartments",
        "url": "https://www.reddit.com/r/UMD/comments/12js4z9/red_flags_about_new_apartments_coming_to_college/",
        "mode": "local",
        "file": "RedFlagsUView.html",
    },
    {
        "name": "yelp",
        "title": "Yelp",
        "url": "https://www.yelp.com/biz/university-view-college-park-2",
        "mode": "local",
        "file": "YelpUView.html",
    },
    {
        "name": "amberstudent",
        "title": "AmberStudent",
        "url": "https://amberstudent.com/places/university-view-college-park-college-park-2411237089448",
        "mode": "scrape",
    },
    {
        "name": "facebook",
        "title": "Facebook (student housing post)",
        "url": "https://www.facebook.com/",
        "mode": "local",
        "file": "FacebookUView.html",
    },
]
