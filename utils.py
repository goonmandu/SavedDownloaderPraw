import os
import sys
import wget
import requests
import praw
import emoji
from credentials import *
from excepts import *
import signal
import json
import hashlib
import shutil

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
    "Armenia", "AM",
    "South Korea", "KR",
    "Bahrain", "BH",
    "Belarus", "BY",
    "Brunei", "BN",
    "Syria", "SY",
    "Saudi Arabia", "SA",
    "Yemen", "YE",
    "Oman", "OM",
    "Eritrea", "ER",
    "Equatorial Guinea", "GQ",
    "Uganda", "UG",
    "Tanzania", "TZ",
    "Iran", "IR",
    "Kuwait", "KW",
    "Qatar", "QA",
    "United Arab Emirates", "AE",
    "Turkmenistan", "TM",
    "Uzbekistan", "UZ",
    "Afghanistan", "AF",
    "Pakistan", "PK",
    "China", "CN",
    "Nepal", "NP",
    "Bangladesh", "BD",
    "Vietnam", "VN",
    "Laos", "LA",
    "Thailand", "TH",
    "Cambodia", "KH",
    "Malaysia", "MY",
    "Indonesia", "ID",
    "North Korea", "KP",  # But no one's gonna be using it here anyway LULW
    "Maldives", "MV"
]

all_countries = json.load(open("countries.json", "r"))


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


def download_requests(addr, path, output_name, ext, reddit_instance, subreddit, post_raw):
    global current_directory
    web_filename = addr.split("/")[-1]

    if "v.redd.it" in addr:
        raise SelfVideoNotSupportedError
    elif "redgifs" in addr:
        ext = "mp4"
        final_filename = f"{output_name}-{web_filename[:6]}.{ext}"  # posts with same title
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
            final_filename = f"{output_name}-glry{image_number}-{web_filename[:6]}.{ext}"
            current_directory = f"{path}/{final_filename}"
            if final_filename in existing_files:
                return
            d_img = open(current_directory, 'wb')
            resp = requests.get(link, headers=requests_header)
            d_img.write(resp.content)
            d_img.close()
            image_number += 1
    elif "twitter" in addr:
        try:
            prev_url: str = post_raw.preview["images"][0]["source"]["url"]
        except AttributeError:
            try:
                prev_url: str = post_raw.media_metadata[len(post_raw.media_metadata)-1]["s"]["u"]
                print(prev_url)
                input()
            except Exception as e:
                print(e)
                print(json.dumps(post_raw))
                return
        download_requests(prev_url,
                          path,
                          output_name,
                          prev_url[prev_url.strip("https://external-preview.redd.it/").find(".")+len("https://external-preview.redd.it/")+1
                                   :prev_url.strip("https://external-preview.redd.it/").find("?")+len("https://external-preview.redd.it/")],
                          reddit_instance,
                          subreddit,
                          post_raw)
    else:
        final_filename = f"{output_name}-{web_filename[:6]}.{ext}"
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
    checkip_response = requests.get("https://checkip.amazonaws.com")
    ipaddress = checkip_response.content.decode("utf-8").rstrip()

    url = f"https://ipinfo.io/{ipaddress}?token=424093cb98c93b"
    try:
        response = requests.get(url)
        data = response.json()
        return data["country"]
    except requests.exceptions.RequestException as e:
        print(e)
        return "Unknown"


def get_fullname_of_country_code(twoltrcode):
    for country in all_countries:
        if country["code"] == twoltrcode:
            return country["name"]
    return "Unknown Country"


def hash_file(file_path):
    """Compute the SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256.update(byte_block)
    return sha256.hexdigest()


def rename_images(directory):
    """Rename all image files in a directory to their hash values with original extensions."""
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp", "gifv", "webp", ".mp4", ".mkv")):
                print(f"Current file: {file}")
                file_path = os.path.join(root, file)
                hash_value = hash_file(file_path)
                extension = os.path.splitext(file)[1]
                new_name = f"{hash_value[:32]}{extension}"  # Use original extension in the renamed file
                new_path = os.path.join(root, new_name)

                # Ensure the new file name does not exceed 255 bytes
                if len(new_path) <= 255:
                    os.rename(file_path, new_path)


def is_substring(sub, full):
    return sub in full


def delete_files_recursive(directory):
    for root, dirs, files in os.walk(directory):
        files.sort(key=len, reverse=True)

        for i in range(len(files)):
            current_file = os.path.splitext(files[i])[0]  # Exclude the file extension
            current_file_path = os.path.join(root, files[i])
            print(f"Checking {current_file_path}")

            if current_file_path.endswith("gifv"):
                os.remove(current_file_path)
                continue

            for j in range(i + 1, len(files)):
                potential_substring = os.path.splitext(files[j])[0]  # Exclude the file extension
                potential_substring_path = os.path.join(root, files[j])

                if is_substring(potential_substring, current_file):
                    if os.path.exists(potential_substring_path):
                        os.remove(potential_substring_path)


def copy_directory(source, destination):
    try:
        # Copy directory recursively
        shutil.copytree(source, destination)
        print(f"Directory '{source}' copied to '{destination}' successfully.")
    except Exception as e:
        print(f"Error: {e}")


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

    post = reddit.submission("15fia9u")


if __name__ == "__main__":
    main()