import os
import sys
import wget
import requests
import praw
import emoji
from credentials import *
from excepts import *
import signal

current_directory = ""
existing_files = []
for root, dirs, file in os.walk(f"{os.getcwd()}/download"):
    for name in file:
        if name not in existing_files:
            existing_files.append(name)

requests_header = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/83.0.4103.97 Safari/537.36"
}


countries_that_censor = [
    "Armenia"
    "South Korea",
    "Bahrain"
    "Belarus",
    "Brunei",
    "Syria",
    "Saudi Arabia",
    "Yemen",
    "Oman",
    "Eritrea"
    "Equatorial Guinea",
    "Uganda",
    "Tanzania",
    "Iran",
    "Kuwait",
    "Qatar",
    "United Arab Emirates",
    "Turkmenistan",
    "Uzbekistan",
    "Afghanistan",
    "Pakistan"
    "China",
    "Nepal",
    "Bangladesh",
    "Vietnam",
    "Laos",
    "Thailand",
    "Cambodia",
    "Malaysia",
    "Indonesia",
    "North Korea",  # But no one's gonna be using it here anyway LULW
    "Maldives"
]


def crash_handler(exit_signal, frame):
    global current_directory
    if current_directory == "":
        exit(0)
    else:
        os.remove(current_directory)
        if exit_signal == signal.SIGINT:
            exit(0)
        else:
            exit(3)


def get_all_downloaded_files():
    ret = []
    for root, dirs, file in os.walk(f"{os.getcwd()}/download"):
        for name in file:
            if name not in ret:
                ret.append(name)
    return ret


def extract_source_redgifs(redgifs_link):
    redgifs_html = requests.get(redgifs_link, headers=requests_header).text
    key = "<meta property=\"og:video\" content=\""
    source_start_index = redgifs_html.find(key) + len(key)
    source_end_index = redgifs_html[source_start_index+len(key):].find("\"") + source_start_index + len(key)
    return redgifs_html[source_start_index:source_end_index]


def extract_source_reddit_gallery(reddit_instance, gallery_link, subreddit):
    raw_json = reddit_instance.request(method="GET", path=f"/r/{subreddit}/comments/{gallery_link.split('/')[-1]}")
    try:
        exts = [value["m"].split("/")[-1] for image, value in raw_json[0]["data"]["children"][0]["data"]["media_metadata"].items()]
        image_ids = [image for image in raw_json[0]["data"]["children"][0]["data"]["media_metadata"]]
        image_links = []
        for i, v in enumerate(exts):
            image_links.append(f"https://i.redd.it/{image_ids[i]}.{v}")
        return image_links
    except AttributeError:
        sys.stderr.write("Post was deleted.")
        return []


def create_directory(path):
    if not os.path.exists(path):
        print(f"Directory {path} was not found. Creating it instead.")
        os.mkdir(path)


def create_subreddit_directory(path):
    create_directory(f"download/{path}")
    create_directory(f"download/{path}/images")
    create_directory(f"download/{path}/comments")


def recurse_comment_tree(comment):
    comment.refresh()
    comment_tree = {'body': comment.body,
                    'author': comment.author.name,
                    'replies': []}
    for reply in comment.replies:
        comment_tree['replies'].append(recurse_comment_tree(reply))
    return comment_tree


def get_all_comments(submission):
    comment_tree = []
    for comment in submission.comments:
        comment_tree.append(recurse_comment_tree(comment))
    return comment_tree


def download_requests(addr, path, output_name, ext, reddit_instance, subreddit):
    global current_directory
    web_filename = addr.split("/")[-1]

    if "v.redd.it" in addr:
        raise SelfVideoNotSupportedError
    elif "redgifs" in addr:
        ext = "mp4"
        final_filename = f"{output_name}-{web_filename[:4]}.{ext}"  # posts with same title
        current_directory = f"{path}/{final_filename}"
        if final_filename in existing_files:
            return
        addr = extract_source_redgifs(addr)
        d_img = open(current_directory, 'wb')
        resp = requests.get(addr, headers=requests_header)
        d_img.write(resp.content)
        d_img.close()
    elif "gallery" in addr:
        image_number = 1
        for link in extract_source_reddit_gallery(reddit_instance, addr, subreddit):
            ext = link.split(".")[-1]
            final_filename = f"{output_name}-glry{image_number}-{web_filename[:4]}.{ext}"
            current_directory = f"{path}/{final_filename}"
            if final_filename in existing_files:
                return
            d_img = open(current_directory, 'wb')
            resp = requests.get(link, headers=requests_header)
            d_img.write(resp.content)
            d_img.close()
            image_number += 1
    else:
        final_filename = f"{output_name}-{web_filename[:4]}.{ext}"
        current_directory = f"{path}/{final_filename}"
        if final_filename in existing_files:
            return
        d_img = open(current_directory, 'wb')
        resp = requests.get(addr, headers=requests_header)
        d_img.write(resp.content)
        d_img.close()


def download_wget(addr, path, output_name):
    wget.download(addr, f"{path}/{output_name}")


def remove_non_ascii(string: str) -> str:
    return ''.join(char for char in string if ord(char) < 128)


def unemojify(string: str) -> str:
    return emoji.demojize(string)


def replace_invalid_chars(filepath: str) -> str:
    return filepath.translate(filepath.maketrans(
        {"\\": "_",
         "/":  "_",
         ":":  "_",
         "*":  "_",
         "?":  "_",
         "\"": "_",
         "<":  "_",
         ">":  "_",
         "|":  "_",
         " ":  "_",
         ".":  "_"}))


def get_current_country():
    api_key = IPSTACK_KEY
    url = f"http://api.ipstack.com/check?access_key={api_key}"
    try:
        response = requests.get(url)
        data = response.json()
        return data["country_name"]
    except requests.exceptions.RequestException:
        return "Unknown"


def main():
    reddit = praw.Reddit(client_id=CLIENT_ID,
                         client_secret=SECRET,
                         password=PASSWORD,
                         username=USERNAME,
                         user_agent=USERAGENT)

    imgur = "https://i.imgur.com/ZwmhVma.jpg"
    ireddit = "https://i.redd.it/2i0b7d3d2ura1.jpg"
    redgifs = "https://www.redgifs.com/watch/leafyglassgrayfox"
    discordcdn = "https://cdn.discordapp.com/attachments/935727169559220356/954682516063801355/Patreon_post_image-36.jpg"
    rule34 = "https://rule34.xxx//samples/6724/sample_e8c7589fbace0156bf8c61a34d057cbc.jpg?7674649"
    catbox = "https://files.catbox.moe/9jsbl9.png"
    gallery = "https://www.reddit.com/gallery/13l1zm4"
    post = reddit.submission("14g8qld").is_self
    print(post)

    #create_directory("test")

    #print(extract_source_reddit_gallery(reddit, gallery, subreddit))


if __name__ == "__main__":
    main()