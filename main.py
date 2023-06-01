from prawcore.exceptions import OAuthException, ResponseException
from postdata import PostData
from utils import *


def main():
    signal.signal(signal.SIGINT, crash_handler)
    posts = int(input("Enter an integer number of saved posts to download, from 1 to 1000. "))
    while not 1 <= posts <= 1000:
        posts = int(input("Make sure that 1 <= (number of posts) <= 1000: "))

    print("Logging in to Reddit...")
    reddit = praw.Reddit(client_id=CLIENT_ID,
                         client_secret=SECRET,
                         password=PASSWORD,
                         username=USERNAME,
                         user_agent=USERAGENT)
    print(f"You're logged in as {USERNAME}.")

    input("Press [Enter] to begin download.")

    create_directory("download")
    processed = 0
    for saved_post in reddit.user.me().saved(limit=posts):
        current = PostData(saved_post, get_comments=False)
        print(f"Downloading #{processed + 1} / {posts}:    {round((processed + 1) * 100 / posts, 1)}%   (r/{current.subreddit}, {current.title if len(current.title) < 24 else current.title[:24]})")
        create_subreddit_directory(current.subreddit)
        sanitized_title = replace_invalid_chars(remove_non_ascii(unemojify(current.title)))
        download_requests(current.url,
                          f"download/{current.subreddit}/images",
                          sanitized_title,
                          current.url.split('.')[-1],
                          reddit,
                          current.subreddit)
        processed += 1
    print("Done.")


if __name__ == "__main__":
    try:
        main()
    except OAuthException:
        sys.stderr.write("Invalid username and/or password.")
        exit(1)
    except ResponseException:
        sys.stderr.write("Invalid Client ID and/or Client Secret.")
        exit(2)
    except SelfVideoNotSupportedError:
        sys.stderr.write("v.redd.it links are not supported at the moment.")
    except ConnectionResetError:
        sys.stderr.write("Connection was censored via SNI filtering.")
