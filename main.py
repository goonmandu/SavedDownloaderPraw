from prawcore.exceptions import OAuthException, ResponseException
from postdata import PostData
from utils import *


def main():
    posts = int(input("Enter an integer number of saved posts to download, from 1 to 1000. "))
    while not 1 <= posts <= 1000:
        posts = int(input("Make sure that 1 <= (number of posts) <= 1000: "))

    print("Logging into Reddit...")
    reddit = praw.Reddit(client_id=CLIENT_ID,
                         client_secret=SECRET,
                         password=PASSWORD,
                         username=USERNAME,
                         user_agent=USERAGENT)
    print(f"You're logged in as {USERNAME}.")

    create_directory("download")

    processed = 0
    for saved_post in reddit.user.me().saved(limit=posts):
        current = PostData(saved_post, get_comments=False)
        print(f"Downloading #{processed + 1} / {posts}:     {round((processed + 1) * 100 / posts, 1)}%    ({current.url})")
        create_subreddit_directory(current.subreddit)
        sanitized_title = replace_invalid_chars(remove_non_ascii(current.title))
        if "v.redd.it" not in current.url:
            download_requests(current.url,
                              f"download/{current.subreddit}/images",
                              sanitized_title,
                              current.url.split('.')[-1],
                              reddit,
                              current.subreddit)
        else:
            sys.stderr.write("Reddit-hosted videos are not supported yet. Skipping...")
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