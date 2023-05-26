import os
import sys
import wget
import requests
import praw
from credentials import *


requests_header = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/83.0.4103.97 Safari/537.36"
}


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
    if "v.redd.it" in addr:
        return  # Reddit-hosted videos are not supported as of right now
    if "redgifs" in addr:
        ext = "mp4"
        addr = extract_source_redgifs(addr)
        d_img = open(f"{path}/{output_name}.{ext}", 'wb')
        resp = requests.get(addr, headers=requests_header)
        d_img.write(resp.content)
        d_img.close()
    elif "gallery" in addr:
        image_number = 1
        for link in extract_source_reddit_gallery(reddit_instance, addr, subreddit):
            ext = link.split(".")[-1]
            d_img = open(f"{path}/{output_name}-glry{image_number}.{ext}", 'wb')
            resp = requests.get(link, headers=requests_header)
            d_img.write(resp.content)
            d_img.close()
            image_number += 1
    else:
        d_img = open(f"{path}/{output_name}.{ext}", 'wb')
        resp = requests.get(addr, headers=requests_header)
        d_img.write(resp.content)
        d_img.close()


def download_wget(addr, path, output_name):
    wget.download(addr, f"{path}/{output_name}")


def remove_non_ascii(string: str) -> str:
    return ''.join(char for char in string if ord(char) < 128)


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
    subreddit = reddit.submission("13l1zm4").subreddit

    create_directory("test")

    print(extract_source_reddit_gallery(reddit, gallery, subreddit))


if __name__ == "__main__":
    main()