"""
User analyzer for fetching and analyzing user history.
Extracted from AIbot_utils.py for better modularity.
"""

from ..config import ContextConfig
from log import logger


class UserAnalyzer:
    """Handles user history and portrait generation"""
    
    def __init__(self, reddit_client):
        self.reddit = reddit_client
        self.config = ContextConfig()
    
    def get_user_history(self, username, sub_user_nickname="用户", 
                        post_limit=None, comment_limit=None):
        """
        Fetch user's recent posts and comments for AI analysis.
        
        Args:
            username: Reddit username to fetch history for
            sub_user_nickname: Nickname prefix for users in this subreddit
            post_limit: Number of recent posts to fetch (uses config default if None)
            comment_limit: Number of recent comments to fetch (uses config default if None)
        
        Returns:
            str: Formatted string containing user's recent activity, empty if error/no content
            
        TODO: Add caching mechanism to avoid repeated API calls for same user within time window
        TODO: Add karma/reputation filtering - prioritize high-karma content
        TODO: Add subreddit-specific weighting for current community activity
        TODO: Filter out bot conversations and low-quality content
        TODO: Implement smart caching strategy with 1-6 hour user history cache
        TODO: Add user profile analysis caching for longer periods (interests, style)
        TODO: Add selective history fetching - skip low-karma or new/throwaway accounts
        TODO: Add rate limiting per user to avoid API abuse
        TODO: Add better content filtering - remove deleted/removed content, prioritize recent high-karma
        TODO: Add privacy and ethics considerations - exclude sensitive subreddits, respect deletion requests
        TODO: Add timeout limits and graceful degradation for user history fetching
        TODO: Add quality metrics tracking - which replies get better engagement with user history
        TODO: Add user type detection for personalization effectiveness monitoring
        """
        # Use config defaults if not specified
        if post_limit is None:
            post_limit = self.config.USER_HISTORY_POST_LIMIT
        if comment_limit is None:
            comment_limit = self.config.USER_HISTORY_COMMENT_LIMIT
            
        try:
            user = self.reddit.redditor(username)
            history_str = ""
            
            # Fetch recent posts
            history_str += self._fetch_user_posts(user, username, sub_user_nickname, post_limit)
            
            # Fetch recent comments  
            history_str += self._fetch_user_comments(user, username, sub_user_nickname, comment_limit)
                
            return history_str.strip()
            
        except Exception as e:
            logger.debug(f"Error fetching user history for {username}: {e}")
            return ""
    
    def _fetch_user_posts(self, user, username, sub_user_nickname, post_limit):
        """Fetch and format user's recent posts"""
        try:
            posts = list(user.submissions.new(limit=post_limit))
            if not posts:
                return ""
                
            history_str = f"{sub_user_nickname} {username} 的近期发帖：\n"
            for post in posts:
                if self._check_content_status(post) == "normal":
                    post_content = f"标题: {post.title}"
                    if post.selftext and post.selftext.strip():
                        # Limit content length using config
                        content_limit = self.config.MAX_POST_CONTENT_LENGTH
                        post_content += f" | 内容: {post.selftext[:content_limit]}"
                    post_content += f" | karma: {post.score} | 社区: r/{post.subreddit}\n"
                    history_str += post_content
            history_str += "\n"
            return history_str
            
        except Exception as e:
            logger.debug(f"Could not fetch posts for user {username}: {e}")
            return ""
    
    def _fetch_user_comments(self, user, username, sub_user_nickname, comment_limit):
        """Fetch and format user's recent comments"""
        try:
            comments = list(user.comments.new(limit=comment_limit))
            if not comments:
                return ""
                
            history_str = f"{sub_user_nickname} {username} 的近期评论：\n"
            for comment in comments:
                if self._check_content_status(comment) == "normal":
                    # Limit comment length using config
                    comment_limit = self.config.MAX_COMMENT_LENGTH
                    comment_text = comment.body[:comment_limit] if len(comment.body) > comment_limit else comment.body
                    comment_content = f"评论: {comment_text} | karma: {comment.score} | 社区: r/{comment.subreddit}\n"
                    history_str += comment_content
            history_str += "\n"
            return history_str
            
        except Exception as e:
            logger.debug(f"Could not fetch comments for user {username}: {e}")
            return ""
    
    def _check_content_status(self, content):
        """
        Check if content is normal, removed, or blocked.
        
        Args:
            content: Reddit content object (submission or comment)
            
        Returns:
            str: "normal", "removed", or "blocked"
        """
        # Import here to avoid circular imports
        removed_content_list = ["[removed]", "[deleted]", "[ Removed by Reddit ]"]
        blocked_content = "[unavailable]"
        
        # Determine content text based on type
        if hasattr(content, 'selftext'):  # Submission
            check_str = content.selftext
        else:  # Comment
            check_str = content.body
            
        if check_str in removed_content_list:
            return "removed"
        elif check_str == blocked_content:
            return "blocked"
        else:
            return "normal"
    
    def analyze_user_patterns(self, history):
        """
        Analyze user posting patterns and interests.
        
        Args:
            history: User history string
            
        Returns:
            dict: Analysis results
            
        TODO: Implement pattern analysis
        TODO: Add cross-thread behavior analysis
        TODO: Add conversation style adaptation based on thread type and community norms
        TODO: Add user reputation/karma consideration for current subreddit specifically
        """
        # Placeholder for future implementation
        return {
            "interests": [],
            "communication_style": "unknown",
            "activity_level": "unknown",
            "expertise_areas": []
        }
