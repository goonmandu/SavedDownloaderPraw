from utils import get_all_comments


class PostData:
    def __init__(self, submission, get_comments=False):
        self.subreddit = submission.subreddit
        self.title = submission.title
        self.url = submission.url
        self.comments = get_all_comments(submission) if get_comments else None
        self.comment_count = submission.num_comments

    def __str__(self):
        return f"r/{self.subreddit}\n" \
               f"{self.title}\n" \
               f"{self.url}\n" \
               f"{self.comment_count} comments"
