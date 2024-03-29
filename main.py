from prawcore.exceptions import OAuthException, ResponseException
from postdata import PostData
from utils import *


def main():
    signal.signal(signal.SIGINT, crash_handler)
    print("Checking country of IP address... ", end="")
    current_country = get_fullname_of_country_code(country_code := get_current_country())
    print(current_country)
    if country_code in countries_that_censor:
        if not input(f"\nWARNING: You are trying to download from an IP from {current_country}.\n"
                     f"Downloads of explicit material may fail due to internet censorship.\n"
                     f"Are you sure you want to continue?\n"
                     f"Enter 'Yes' to download anyway, or anything else to quit. ") == "Yes":
            print("\nDownload aborted.")
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
        print(f"Skipping until #{skip}")
    else:
        skip = 0

    create_directory("download")
    for idx, saved_post in enumerate(reddit.user.me().saved(limit=posts)):
        if isinstance(saved_post, praw.models.Comment):
            print(f"Downloading #{idx + 1} / {posts}: Saved comment. Skipping...")
            continue
        if idx < skip - 1:
            print(f"Skipping over #{idx+1}", end="\r")
            continue
        try:
            current = PostData(saved_post, get_comments=False)
            print(f"Downloading #{idx + 1} / {posts}:    {round((idx + 1) * 100 / posts, 1)}%   "
                  f"[{saved_post.id}] "
                  f"(r/{current.subreddit}, {current.title if len(current.title) < 50 else current.title[:50]})")

            if saved_post.is_self:
                sys.stderr.write("Found a post without any attached media. Skipping.")
                continue

            create_subreddit_directory(current.subreddit)
            sanitized_title = replace_invalid_chars(remove_non_ascii(unemojify(current.title)))
            if len(sanitized_title) > 127:
                sanitized_title = sanitized_title[:127]
            download_requests(current.url,
                              f"download/{current.subreddit}/images",
                              sanitized_title,
                              current.url.split('.')[-1],
                              reddit,
                              current.subreddit,
                              saved_post)

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

        except Exception as e:
            sys.stderr.write(f"Unknown error:\n{e}")

    print("Done.")

    if input("To delete duplicate media downloaded prior to the 6-character identifier, enter \"Y\". ") == "Y":
        delete_files_recursive("./download")

    print("Done.")

if __name__ == "__main__":
    main()