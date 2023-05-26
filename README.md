# Reddit Saved Media Downloader
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
- [ ] Universal download function, instead of current implementation of `download_requests`
- [ ] Add features from RSD V1 (e.g. duplicates filter)
- [ ] Skip already downloaded media