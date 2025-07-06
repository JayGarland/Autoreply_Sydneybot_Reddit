"""Reddit API client wrapper."""
import praw
import random
from typing import List, Optional
from config import conf
from log import logger


class RedditClient:
    """Wrapper for Reddit API client with bot-specific functionality."""
    
    def __init__(self):
        self.reddit = None
        self.subreddit = None
        self.current_subreddit_name = None
        self.subreddit_names = []
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Reddit client with credentials."""
        bot_name = conf().get('bot_name')
        password = conf().get('password')
        client_id = conf().get('client_id')
        client_secret = conf().get('client_secret')
        user_agent = "autoreply bot created by u/Chinese_Dictator."
        
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            password=password,
            user_agent=user_agent,
            username=bot_name
        )
        
        # Get subreddit names
        target_subreddits = conf().get('TargetSubreddits')
        self.subreddit_names = [list(target_subreddits[i].keys())[0] 
                               for i in range(len(target_subreddits))]
        
        # Set random subreddit
        self.set_random_subreddit()
    
    def set_random_subreddit(self):
        """Set a random subreddit as current."""
        self.current_subreddit_name = random.choice(self.subreddit_names)
        self.subreddit = self.reddit.subreddit(self.current_subreddit_name)
        logger.info(f"Set current subreddit to: {self.current_subreddit_name}")
    
    def get_subreddit_config(self) -> dict:
        """Get configuration for current subreddit."""
        for reddit_config in conf().get("TargetSubreddits"):
            if self.current_subreddit_name in reddit_config:
                return reddit_config[self.current_subreddit_name]
        return {}
    
    def get_comment(self, comment_id: str):
        """Get comment by ID."""
        return self.reddit.comment(comment_id)
    
    def get_submission(self, submission_id: str):
        """Get submission by ID."""
        return self.reddit.submission(submission_id)
    
    def get_new_submissions(self, limit: int = 10) -> List:
        """Get new submissions from current subreddit."""
        return list(self.subreddit.new(limit=limit))
    
    def get_comments(self, limit: int = 50) -> List:
        """Get comments from current subreddit."""
        return list(self.subreddit.comments(limit=limit))
