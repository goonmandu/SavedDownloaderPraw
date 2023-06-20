# Reddit Saved Media Downloader
##  This project is under indefinite hiatus because of [Reddit's API changes](https://redd.it/145bram). Development will continue when API access is normalized.
TLDR:<br>
1. Reddit is effectively denying access to its API for third-party Reddit browsers (e.g. <img src="https://play-lh.googleusercontent.com/GF71STDEmTKhbEexCYbePXAjYym_ee8E6WR7_R8jr5_Xf10jfL0Kibkjfl33zDrJBw"  width="15"> Boost for Reddit, <img src="https://play-lh.googleusercontent.com/7eZdn-k3hT4CyxcEztIRPgZiaCS13bbombYFnonJvMRttjHFUzVSkJce61x6pyPiHQs"  width="15"> Reddit is Fun, <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Apollo_app_logo.svg/1200px-Apollo_app_logo.svg.png"  width="15"> Apollo) by demanding insanely high API pricing.
2. Reddit is also censoring NSFW from the API that third-party Reddit browsers use. Reddit CEO [u/spez](https://reddit.com/u/spez) explained that this is to obey regulations regarding serving pornography to minors. However, the official Reddit app is still going to show NSFW. Go figure.

While this script is unaffected by these API changes (due to it not being a Reddit client), its functionality will be severely undermined due to the subreddits participating in the Reddit Blackout protest, which I wholeheartedly support.

Current version: [**0.2.0**](CHANGELOG.md)

Downloads images and videos from the posts that you have saved on your Reddit account.<br>
This is a PRAW rewrite of the scuffed-as-hell original version of the [Reddit Saved Downloader](https://github.com/goonmandu/saved_downloader) that I wrote two years ago.<br>
I will add utility functions of the original code to this rewrite eventually.

## How to use
1. Create your Reddit app.
    - I'm too tired today to explain detailed steps. I'll get to writing this someday.
2. `pip3 install -r requirements.txt`
3. Make a `credentials.py` file in the same directory as `main.py` with the following format:
    - **IMPORTANT** While not mission-critical, leave `USERAGENT` as is. At least make sure that it is not empty.
    ```py
    USERNAME = "Your Reddit username"
    PASSWORD = "Your Reddit password"
    CLIENT_ID = "The app's Client ID"
    SECRET = "The app's Client Secret"
    USERAGENT = "Reddit Saved Downloader PRAW Rewrite"
    ```
4. `python3 main.py`

## TODO
- [ ] Add comment scraping
- [ ] Pipe log to file
- [ ] <strike>Universal download function, instead of current implementation of `download_requests`</strike><sup>[1](#footnote_1)</sup>
- [x] Add features from RSD V1 (e.g. duplicates filter)
- [x] Skip already downloaded media

<a name="footnote_1">1</a>: Unrealistic goal, scrapped. Different websites have different download methods and would require separate functions for each website, which `download_requests` already achieves.