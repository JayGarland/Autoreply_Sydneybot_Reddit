import praw
import json
import datetime
import os
import sys
from pathlib import Path

# Ensure repo root (contains config.py) is importable when script is run directly
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from config import logger, conf

# --- CONFIGURATION ---
REDDIT_CLIENT_ID = conf().get("client_id")
REDDIT_CLIENT_SECRET = conf().get("client_secret")
REDDIT_USERNAME = conf().get("bot_name")
REDDIT_PASSWORD = conf().get("password")
REDDIT_USER_AGENT = "subreddit-style-crawler by u/6uttslapper"
POST_LIMIT = 30  # Number of posts to fetch
MIN_AUTHOR_ACCOUNT_AGE_DAYS = 30  # Minimum account age for authors

# --- INIT ---
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python DataCollection.py <subredditname>")
        sys.exit(1)
    SUBREDDIT_NAME = sys.argv[1]
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT,
        username=REDDIT_USERNAME,
        password=REDDIT_PASSWORD
    )

    subreddit = reddit.subreddit(SUBREDDIT_NAME)
    
    # Check if subreddit is accessible
    try:
        subreddit_name = subreddit.display_name
        print(f"Accessing r/{subreddit_name}...")
    except Exception as e:
        print(f"Error accessing subreddit: {e}")
        print("The subreddit might be private, banned, or quarantined.")
        sys.exit(1)
    
    one_month_ago = datetime.datetime.utcnow() - datetime.timedelta(days=30)
    min_author_account_age = datetime.datetime.utcnow() - datetime.timedelta(days=MIN_AUTHOR_ACCOUNT_AGE_DAYS)

    data = []

    try:
        posts = subreddit.top(limit=POST_LIMIT)
    except Exception as e:
        print(f"Error fetching posts: {e}")
        print("This might be due to:")
        print("1. The subreddit is private or quarantined")
        print("2. Rate limiting from Reddit API")
        print("3. Authentication issues")
        sys.exit(1)
    
    posts_fetched = 0
    posts_filtered = 0
    
    for post in posts:
        posts_fetched += 1
        
        # Filter by post age (created_utc is in seconds)
        post_time = datetime.datetime.utcfromtimestamp(post.created_utc)
        if post_time < one_month_ago:
            posts_filtered += 1
            continue

        # Filter out posts containing preview.redd.it
        if "https://preview.redd.it" in post.selftext or "https://preview.redd.it" in post.title:
            posts_filtered += 1
            continue

        # Filter by author account age
        try:
            author_created_utc = post.author.created_utc
            author_created = datetime.datetime.utcfromtimestamp(author_created_utc)
            if author_created > min_author_account_age:
                posts_filtered += 1
                continue
        except Exception:
            # If author is deleted or unavailable, skip
            posts_filtered += 1
            continue

        post_data = {
            "title": post.title,
            "selftext": post.selftext,
            "author": str(post.author),
            "score": post.score,
            "comments": []
        }

        post.comments.replace_more(limit=0)
        for comment in post.comments.list():
            # Only top-level comments, skip deleted/removed
            if comment.parent_id != post.name or comment.body in ["[deleted]", "[removed]"]:
                continue
            # Filter out comments containing preview.redd.it
            if "https://preview.redd.it" in comment.body:
                continue
            # Filter by comment score
            if comment.score < 5:
                continue
            # Filter by comment author account age
            try:
                comment_author_created_utc = comment.author.created_utc
                comment_author_created = datetime.datetime.utcfromtimestamp(comment_author_created_utc)
                if comment_author_created > min_author_account_age:
                    continue
            except Exception:
                continue

            post_data["comments"].append({
                "body": comment.body,
                "author": str(comment.author),
                "score": comment.score
            })

        data.append(post_data)

    # Save to file
    subreddit_data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', f'{SUBREDDIT_NAME}_data')
    raw_dir = os.path.join(subreddit_data_dir, 'raw')
    processed_dir = os.path.join(subreddit_data_dir, 'processed')
    summaries_dir = os.path.join(processed_dir, 'summaries')

    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(summaries_dir, exist_ok=True)

    with open(os.path.join(raw_dir, "top_posts_last_month.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Fetched {posts_fetched} posts from r/{SUBREDDIT_NAME}")
    print(f"Filtered out {posts_filtered} posts")
    print(f"Collected {len(data)} posts from r/{SUBREDDIT_NAME} (top, last month)")
