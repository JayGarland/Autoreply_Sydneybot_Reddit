"""
Subreddit context provider.
Handles subreddit background information and community context.
"""

from ..config import ContextConfig


class SubredditContextProvider:
    """Handles subreddit background and community info"""
    
    def __init__(self):
        self.config = ContextConfig()
    
    def get_subreddit_context(self, subreddit_name):
        """
        Get subreddit background context.
        
        Args:
            subreddit_name: Name of the subreddit
            
        Returns:
            str: Formatted subreddit context
            
        TODO: Add subreddit culture analysis
        TODO: Add community norms detection  
        TODO: Add hot topics and trends
        TODO: Add demographic analysis
        TODO: Add temporal context (time of day/week patterns)
        TODO: Add seasonal relevance and current events
        """
        return f"当前 r/{subreddit_name} 社区背景信息。"
    
    def get_submission_overview(self, submission):
        """
        Get submission overview with engagement metrics.
        
        Args:
            submission: Reddit submission object
            
        Returns:
            str: Formatted submission overview
            
        TODO: Add submission overview with engagement metrics and discussion trends
        TODO: Add hot topics and current events relevant to community
        """
        context = f"以下是{submission.author} 发的帖子。\n"
        context += f"帖子标题是{submission.title}"
        
        if submission.selftext:
            # Limit content length using config
            content_limit = self.config.MAX_SUBMISSION_CONTENT_LENGTH
            content = submission.selftext[:content_limit]
            context += f"，内容是{content}"
            
        context += f" | karma: {submission.score} | 评论数: {submission.num_comments}"
        
        return context
    
    def get_submission_list_context(self, submission_list, sub_user_nickname, subreddit_name):
        """
        Build context from a list of submissions for subreddit overview.
        
        Args:
            submission_list: List of Reddit submission objects
            sub_user_nickname: User nickname for this subreddit
            subreddit_name: Name of the subreddit
            
        Returns:
            str: Formatted submission list context
        """
        context_str = f'[system](#context)\n当前 r/{subreddit_name} sub 中的帖子有：\n\n'
        
        for submission in submission_list:
            # Check submission status (would need to import check_status function)
            # For now, skip this check and let calling code handle it
            submission_str = f"{sub_user_nickname} {submission.author} 发布了标题为{submission.title}的帖子"
            
            if submission.selftext:
                # Limit content length using config
                content = submission.selftext[:self.config.MAX_CONTEXT_LENGTH]
                submission_str += f"，内容是{content}"
                
            submission_str += "\n"
            context_str += submission_str
            
        return context_str
