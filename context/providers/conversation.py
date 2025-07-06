"""
Conversation context provider.
Handles thread conversation and submission context building.
"""

from ..config import ContextConfig
from log import logger


class ConversationContextProvider:
    """Handles thread conversation and submission context"""
    
    def __init__(self, reddit_client):
        self.reddit = reddit_client
        self.config = ContextConfig()
    
    def get_submission_context(self, submission, sub_user_nickname):
        """
        Extract submission info, title, content.
        
        Args:
            submission: Reddit submission object
            sub_user_nickname: User nickname for this subreddit
            
        Returns:
            str: Formatted submission context
        """
        context = f"以下是{sub_user_nickname} {submission.author} 发的帖子。\n"
        context += f"帖子标题是{submission.title}"
        
        if submission.selftext:
            # Use config for content length limit
            content_limit = self.config.MAX_SUBMISSION_CONTENT_LENGTH
            context += f"，内容是{submission.selftext[:content_limit]}"
            
        return context
    
    def get_conversation_thread(self, comment, ancestors, sub_user_nickname, 
                              bot_nickname, bot_name, bot_name_list):
        """
        Handle complex ancestor/reply logic for comment threads.
        
        Args:
            comment: The comment being replied to
            ancestors: List of ancestor comments
            sub_user_nickname: User nickname for this subreddit
            bot_nickname: Bot's nickname
            bot_name: Bot's username
            bot_name_list: List of bot usernames
            
        Returns:
            str: Formatted conversation thread context
            
        TODO: Add enhanced multi-thread context collection
        TODO: Add parallel discussion thread analysis
        TODO: Add topic clustering and sentiment flow tracking across threads
        TODO: Add smart context selection based on relevance scoring and engagement filtering
        """
        submission = self.reddit.submission(comment.link_id[3:])
        context_str = f"以下是{sub_user_nickname} {submission.author} 发的帖子。\n"
        context_str += f'帖子标题是"{submission.title}"'
        
        if submission.selftext:
            context_str += f'，内容是"{submission.selftext}"'
        context_str += "\n"
        
        # Build conversation thread
        first_comment = True
        replied_to_author = submission.author
        ancestors.insert(0, comment)
        
        for ancestor in reversed(ancestors):
            context_str += self._format_ancestor_comment(
                ancestor, replied_to_author, first_comment,
                sub_user_nickname, bot_nickname, bot_name, bot_name_list
            )
            replied_to_author = ancestor.author
            first_comment = False
            
        return context_str
    
    def get_related_comments(self, submission, sub_user_nickname, bot_name_list):
        """
        Get top comments and parallel discussions.
        
        Args:
            submission: Reddit submission object
            sub_user_nickname: User nickname for this subreddit  
            bot_name_list: List of bot usernames to filter out
            
        Returns:
            str: Formatted related comments context
            
        TODO: Replace current top_comments with multi-thread context system
        TODO: Implement thread summaries instead of just top comments
        TODO: Add dynamic context building based on current user's likely interests
        TODO: Add performance optimization - cache submission comment trees, smart depth limiting
        """
        context_str = f"\n\n在此帖子下还有一些其他{sub_user_nickname}的评论：\n"
        
        try:
            submission.comment_sort = "top"
            top_comments = submission.comments.list()[:self.config.TOP_COMMENTS_LIMIT]
            
            for comment in top_comments:
                if comment.author not in bot_name_list:
                    context_str += f"{comment.body}({comment.score}karma)\n"
                    
        except Exception as e:
            logger.warning(f"Could not fetch related comments: {e}")
            
        return context_str + "\n\n"
    
    def _format_ancestor_comment(self, ancestor, replied_to_author, first_comment,
                               sub_user_nickname, bot_nickname, bot_name, bot_name_list):
        """Format a single ancestor comment in the conversation thread"""
        from AIbot_utils import remove_bot_statement  # Import here to avoid circular imports
        
        if first_comment:
            if ancestor.author in bot_name_list:
                if ancestor.author == bot_name:
                    return f"{bot_nickname} 评论 {sub_user_nickname} {replied_to_author} 的帖子说{remove_bot_statement(ancestor.body)}\n"
                else:
                    return f"{sub_user_nickname} {ancestor.author} 评论 {replied_to_author} 的帖子说{remove_bot_statement(ancestor.body)}\n"
            elif replied_to_author == bot_name:
                return f"{sub_user_nickname} {ancestor.author} 评论 {bot_nickname} 的帖子说{ancestor.body}\n"
            else:
                return f"{sub_user_nickname} {ancestor.author} 评论 {replied_to_author} 的帖子说{ancestor.body}\n"
        else:
            if ancestor.author in bot_name_list:
                if ancestor.author == bot_name:
                    return f"{bot_nickname} 评论 {sub_user_nickname} {replied_to_author} 的回复说{remove_bot_statement(ancestor.body)}\n"
                else:
                    return f"{sub_user_nickname} {ancestor.author} 评论 {replied_to_author} 的回复说{remove_bot_statement(ancestor.body)}\n"
            elif replied_to_author == bot_name:
                return f"{sub_user_nickname} {ancestor.author} 评论 {bot_nickname} 的回复说{ancestor.body}\n"
            else:
                return f"{sub_user_nickname} {ancestor.author} 评论 {replied_to_author} 的回复说{ancestor.body}\n"
