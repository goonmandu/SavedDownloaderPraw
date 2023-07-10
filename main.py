from prawcore.exceptions import OAuthException, ResponseException
from postdata import PostData
from utils import *


def main():
    signal.signal(signal.SIGINT, crash_handler)
    if (current_country := get_current_country()) in countries_that_censor:
        if not input(f"WARNING: You are trying to download from {'an' if current_country[0].lower() in ['a', 'e' ,'i', 'o', 'u'] else 'a'} "
                     f"{current_country} IP.\n"
                     f"Downloads of explicit material may fail due to internet censorship.\n"
                     f"Are you sure you want to continue?\n"
                     f"Enter 'Yes' to download anyway, or anything else to quit. ") == "Yes":
            exit(4)

    posts = int(input("Enter an integer number of saved posts to download, from 1 to 1000. "))
    while not 1 <= posts <= 1000:
        posts = int(input("Make sure that 1 <= (number of posts) <= 1000: "))

    try:
        print("Logging in to Reddit...")
        reddit = praw.Reddit(client_id=CLIENT_ID,
                             client_secret=SECRET,
                             password=PASSWORD,
                             username=USERNAME,
                             user_agent=USERAGENT)
        print(f"You're logged in as {USERNAME}.")
    except OAuthException:
        sys.stderr.write("Invalid username and/or password.\n")
        exit(1)

    if (debug := input("Press [Enter] to begin download.")).lower().startswith("from"):
        skip = int(debug[4:])
    else:
        skip = 0

    create_directory("download")
    for idx, saved_post in enumerate(reddit.user.me().saved(limit=posts)):
        if idx < skip - 1:
            continue
        try:
            current = PostData(saved_post, get_comments=False)
            print(f"Downloading #{idx + 1} / {posts}:    {round((idx + 1) * 100 / posts, 1)}%   "
                  f"(r/{current.subreddit}, {current.title if len(current.title) < 24 else current.title[:24]}) "
                  f"[{saved_post.id}]")

            if saved_post.is_self:
                sys.stderr.write("Found a post without any attached media. Skipping.")
                continue

            create_subreddit_directory(current.subreddit)
            sanitized_title = replace_invalid_chars(remove_non_ascii(unemojify(current.title)))
            download_requests(current.url,
                              f"download/{current.subreddit}/images",
                              sanitized_title,
                              current.url.split('.')[-1],
                              reddit,
                              current.subreddit)

        except ResponseException as e:  # Handle HTTP errors
            exception_string = str(e)
            if "404" in exception_string:
                sys.stderr.write("Received HTTP 404.\n")
            elif "403" in exception_string:
                sys.stderr.write("Received HTTP 403. Check your Reddit API credentials.\n")
            else:
                sys.stderr.write(exception_string)

        except SelfVideoNotSupportedError:  # Self Videos
            sys.stderr.write("v.redd.it links are not supported at the moment.\n")

        except ConnectionResetError:  # Internet Censorship
            sys.stderr.write("Connection was censored via SNI filtering.\n")

        except requests.exceptions.MissingSchema as e:
            sys.stderr.write(f"Unknown error:\n{e}")

    print("Done.")


if __name__ == "__main__":
    main()